"""Main Module for Job Tracker."""

import argparse
import json
import os
import re

import psycopg
import pyperclip
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

"""Input: Copy and pasted description of job just from clipboard
Output: Added job entry to database.

Always been a CLI warrior will just make a CLI for this

Steps:
1. Create a means of just acqurign the copied job description from clipboard
2. Using langchain make it analyze the description and put it in format that can be added to database
3. Utilize the schema you have to help with context for model
4. Have Ollama model attempt to create the job entry as a SQL query
5. Add a verification step to allow the user to view and confirm the job entry
5. Add the job entry to the database
6. Return a success message to the user
"""


def _read_schema_from_file(filepath: str) -> str:
    with open(filepath) as file:
        schema = file.read()
        # Remove the id column definition using a regular expression
        schema = re.sub(r"\s*id\s+SERIAL\s+PRIMARY\s+KEY,\s*", "\n    ", schema, flags=re.IGNORECASE)
        return schema


def _analyze_job_description(description: str, schema: str) -> str:
    template = """
    You are a helpful assistant designed to parse job descriptions
    and extract relevant information for a job application tracker. Your output
    MUST be a valid JSON object CONFIRMING to the PROVIDED schema. If a field
    cannot be extracted, its value in the JSON MUST be null. Do not include any
    explanation or commentary outside the JSON object.

    Database Schema:
    ```sql
    {schema}
    ```

    Job Description:
    ```
    {description}
    ```

    Instructions:

    1.  **Direct Extraction:** Extract explicit information (e.g., company name,
    position title, application date, application status, job link, application
    method, salary range, contact info) directly from the job description. If a
    piece of information is explicitly provided, use *that exact wording* if possible.
    Otherwise leave as null.

    2.  **Required Skills:** Extract information related to *required* and
    *preferred/desired* skills from sections typically labeled as:
        *   Required Skills
        *   Required Qualifications
        *   Minimum Qualifications
        *   Basic Qualifications
        *   Essential Skills
        *   Must Have
        *   Requirements
        *   Preferred Qualifications
        *   Desired Skills
        *   Bonus Points For
        *   Nice to Have
        List all of these skills as a comma-separated string in the
        "required_skills" field.

    3.  **Inference (Use with Caution):** Infer implicit information (e.g.,
    company problem, company priorities, value proposition) *only when strongly
    implied* by the job description. If there's ambiguity or no clear implication,
    set the corresponding JSON value to null.

    Guidelines for Inference:

    *   **Company Problem:** Identify the core problem the company aims to solve
    with this role. Focus on the pain points or challenges the company faces.
    *   **Company Priorities:** Determine the company's key objectives related
    to this role. These are often related to business goals or product improvements.
    *   **Value Proposition (What they want YOU to bring):** Summarize the
    primary value the company expects from the candidate in this role.
    *   **ONLY WORK WITH THE SCHEMA PROVIDED:** Do not add or remove fields from
    the schema. If a field cannot be extracted, set its value to null.

    Output (DON'T MAKE KEYS OUTSIDE OF THE SCHEMA):
    ```json
    """

    prompt = ChatPromptTemplate.from_template(template)
    model = OllamaLLM(model="llama3.2", num_ctx=14000)
    chain = prompt | model
    response = chain.invoke({"description": description, "schema": schema})

    return response


def _generate_sql(json_data: str) -> tuple[str, list]:
    """Generate a parameterized SQL query from JSON data.

    Return:
        a tuple of (query string, parameters list).
    """
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON received: {e}")
        return None

    columns = list(data.keys())
    values = list(data.values())

    # Create the parameterized query
    placeholders = ["%s" for _ in values]
    query = f"INSERT INTO jobs ({', '.join(columns)}) VALUES ({', '.join(placeholders)});"  # noqa: S608

    print("Generated SQL:\n", query)
    print("With values:", values)

    confirmation = input("Confirm adding this entry? (y/n): ")
    if confirmation.lower() != "y":
        return None

    return query, values


def _add_to_database(sql_data: tuple[str, list]) -> None:
    """Add a job to the database using a parameterized query.

    Args:
        sql_data: Tuple of (query string, parameters list)
    """
    if not sql_data:
        print("Improper SQL Data Syntax")
        return

    if not load_dotenv():
        print("Was not able to load .env file")
        return

    query, params = sql_data
    database_url = os.environ.get("DATABASE_URL")

    try:
        conn = psycopg.connect(database_url)
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
        print("Job added to database successfully!")
    except psycopg.Error as e:
        print(f"Error adding to database: {e}")
    finally:
        if conn:
            conn.close()


def main() -> None:
    """Main function to parse job description and add to database."""
    parser = argparse.ArgumentParser(description="Parse job description and add to database")
    parser.add_argument("--schema", type=str, help="Path to the database schema file", default="init.sql")
    args = parser.parse_args()

    schema = _read_schema_from_file(args.schema)
    job_description_from_clipboard = pyperclip.paste()
    job_query = _analyze_job_description(job_description_from_clipboard, schema)
    sql_data = _generate_sql(job_query)
    if sql_data:
        _add_to_database(sql_data)


if __name__ == "__main__":
    main()

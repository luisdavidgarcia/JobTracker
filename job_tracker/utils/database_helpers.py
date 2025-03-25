"""Helper functions for the job tracker database."""

import json
import os
import re
import sys
from datetime import datetime

import psycopg
import pyperclip
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


def _read_schema_from_file(filepath: str) -> str:
    with open(filepath) as file:
        schema = file.read()
        # Remove the id column definition using a regular expression
        schema = re.sub(
            r"\s*id\s+SERIAL\s+PRIMARY\s+KEY,\s*",
            "\n    ",
            schema,
            flags=re.IGNORECASE,
        )
        return schema


def _save_job_description(schema: str) -> None:
    """Save job description from clipboard."""
    print("Saving job description from clipboard...", flush=True)

    job_description_from_clipboard = pyperclip.paste()

    # Force a clipboard refresh - this tricks the system into thinking something changed
    # Store current clipboard content temporarily
    temp_content = job_description_from_clipboard
    pyperclip.copy("")  # Copy empty string
    pyperclip.copy(temp_content)  # Copy original content back

    job_query = _analyze_job_description(job_description_from_clipboard, schema)
    sql_data = _generate_sql(job_query)
    if sql_data:
        _add_to_database(sql_data)
    else:
        print("\nJob not added to database. Try again...\n")
        print("Listening for hotkeys...\n")


def _quit_program() -> bool:
    """Quit the program."""
    print("\nGreat work today! Quitting program now...")
    sys.exit(0)
    return False


def _analyze_job_description(
    description: str,
    schema: str,
    model: str = "llama3.2",
    num_ctx: int = 4096,
) -> dict:
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

    1.  **Direct Extraction:** Extract the company name and position title
    directly from the job description. If a
    piece of information is explicitly provided, use *that exact wording* if possible.
    Otherwise leave as null.

    Output (DON'T MAKE KEYS OUTSIDE OF THE SCHEMA):
    ```json
    """

    prompt = ChatPromptTemplate.from_template(template)
    model = OllamaLLM(model=model, num_ctx=num_ctx)
    chain = prompt | model

    try:
        response = chain.invoke({"description": description, "schema": schema})
        json_response = json.loads(response)
        json_response["original_description"] = description
        json_response["created_at"] = datetime.now().isoformat()
        return json_response
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw response: {response}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}


def _generate_sql(job_data: dict) -> tuple[str, list] | None:
    """Generate a parameterized SQL query from job data (dictionary)."""
    try:
        columns = list(job_data.keys())
        values = list(job_data.values())

        # Create the parameterized query
        placeholders = ["%s" for _ in values]
        query = f"INSERT INTO jobs ({', '.join(columns)}) VALUES ({', '.join(placeholders)});"  # noqa: S608

        print("Generated SQL:\n", query, flush=True)
        print("With values:\n", values, flush=True)

        confirmation = input("Confirm adding this entry? (y/n): ")
        if confirmation == "y":
            return query, values

        return None

    except Exception as e:
        print(f"Error generating SQL: {e}")
        return None


def _add_to_database(sql_data: tuple[str, list] | None) -> None:
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
        print("\nJob added to database successfully!")
        print("Listening for hotkeys...\n")
    except psycopg.Error as e:
        print(f"Error adding to database: {e}")
    finally:
        if conn:
            conn.close()

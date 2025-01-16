# Tasks to do (Get it Done first then iterate)
'''
Input: Copy and pasted description of job just from clipboard 
Output: Added job entry to database

Always been a CLI warrior will just make a CLI for this

Steps:
1. Create a means of just acqurign the copied job description from clipboard
2. Using langchain make it analyze the description and put it in format that can be added to database
3. Utilize the schema you have to help with context for model
4. Have Ollama model attempt to create the job entry as a SQL query
5. Add a verification step to allow the user to view and confirm the job entry
5. Add the job entry to the database
6. Return a success message to the user
'''

import argparse
import os
import re
import pyperclip
import psycopg
import json
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


def read_schema_from_file(filepath):
    with open(filepath, 'r') as file:
        schema = file.read()
        # Remove the id column definition using a regular expression
        schema = re.sub(r"\s*id\s+SERIAL\s+PRIMARY\s+KEY,\s*", "\n    ", schema, flags=re.IGNORECASE)
        return schema 
    
def analyze_job_description(description, schema):
    template = """
    You are a helpful assistant designed to parse job descriptions 
    and extract relevant information for a job application tracker. Your output 
    MUST be a valid JSON object conforming to the provided schema. If a field 
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

    Output:
    ```json
    """

    prompt = ChatPromptTemplate.from_template(template)
    model = OllamaLLM(model="llama3.2", num_ctx=8192)
    chain = prompt | model
    response = chain.invoke({"description": description, "schema": schema})

    return response

def generate_sql(json_data):
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON received: {e}")
        return None
    columns = ", ".join(data.keys())
    values = ", ".join([f"'{v}'" if v else "NULL" for v in data.values()])
    sql = f"INSERT INTO jobs ({columns}) VALUES ({values});"
    print("Generated SQL:\n", sql)

    confirmation = input("Confirm adding this entry? (y/n): ")
    if confirmation.lower() != 'y':
        return None
    return sql

def add_to_database(sql):
    DATABASE_URL = os.environ.get("DATABASE_URL")
    try:
        conn = psycopg.connect(DATABASE_URL)
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()
        print("Job added to database successfully!")
    except psycopg.Error as e:
        print(f"Error adding to database: {e}")
    finally:
        if conn:
            conn.close()

def main():
    parser = argparse.ArgumentParser(description="Parse job description and add to database")
    parser.add_argument("--schema", type=str, help="Path to the database schema file", default="init.sql")
    args = parser.parse_args()

    schema = read_schema_from_file(args.schema)
    job_description_from_clipboard = pyperclip.paste()
    job_query = analyze_job_description(job_description_from_clipboard, schema)
    sql = generate_sql(job_query)
    if sql:
        add_to_database(sql)

if __name__ == "__main__":
    main()
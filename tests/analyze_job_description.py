"""Module for analyzing job descriptions using LangChain and OllamaLLM."""

import pyperclip
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


def _read_schema_from_file(filepath: str) -> str:
    with open(filepath) as file:
        schema = file.read()
        return schema


def _analyze_job_description(description: str, schema: str) -> dict:
    template = """
    You are a helpful assistant designed to parse job descriptions and extract
    relevant information for a job application tracker. Your output MUST be a
    valid JSON object conforming to the provided schema. If a field cannot be
    extracted, its value in the JSON MUST be null. Do not include any
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

    2.  **Required Skills and Experience:** Extract information related to
    required skills and experience from sections typically labeled as:
        *   Required Skills
        *   Required Qualifications
        *   Minimum Qualifications
        *   Basic Qualifications
        *   Essential Skills
        *   Must Have
        *   Requirements
        List these as a comma-separated string in the "required_skills" and
        "required_experience" fields, respectively.

    3.  **Preferred/Desired Skills:** Extract information related to preferred
    or desired skills from sections typically labeled as:
        *   Preferred Qualifications
        *   Desired Skills
        *   Bonus Points For
        *   Nice to Have
        Include these in the "missing_skills" field as a comma-separated string,
        indicating that these are not strictly required.

    4.  **Inference (Use with Caution):** Infer implicit information (e.g.,
    company problem, company priorities, value proposition) *only when strongly
    implied* by the job description. If there's ambiguity or no clear implication,
    set the corresponding JSON value to null.

    Guidelines for Inference:

    *   **Company Problem:** Identify the core problem the company aims to solve
    with this role. Focus on the pain points or challenges the company faces.
    *   **Company Priorities:** Determine the company's key objectives related to
    this role. These are often related to business goals or product improvements.
    *   **Value Proposition (What they want YOU to bring):** Summarize the primary
    value the company expects from the candidate in this role.

    Output:
    ```json
    """

    prompt = ChatPromptTemplate.from_template(template)

    model = OllamaLLM(model="llama3.2", num_ctx=8192)

    chain = prompt | model

    response = chain.invoke({"description": description, "schema": schema})

    return response


def main() -> None:
    """Main function to read schema, get job description from clipboard, and analyze it."""
    schema = _read_schema_from_file("../init.sql")
    job_description_from_clipboard = pyperclip.paste()
    job_query = _analyze_job_description(job_description_from_clipboard, schema)
    print(job_query)


if __name__ == "__main__":
    main()

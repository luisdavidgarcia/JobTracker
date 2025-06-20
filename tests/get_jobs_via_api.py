"""Test with JobsAPI to Obtain Jobs to Apply For."""

import os
from typing import Any

import requests

APIJOBS_KEY = os.getenv("APIJOBS_KEY")
if not APIJOBS_KEY:
    raise ValueError("Please set the APIJOBS_KEY environment variable.")


def _search_jobs(
    position: str,
    country: str = "United States",
    employment_type: str = "Full Time",
    language: str = "English",
) -> dict[str, Any]:
    """Search for jobs using the API."""
    url = "https://api.apijobs.dev/v1/job/search"
    headers = {
        "apikey": APIJOBS_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "q": position,
        "location": {
            "country": country,
        },
        "employment_type": employment_type,
        "language": language,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {}


def _save_job_details_to_file(jobs: list[dict[str, Any]], filename: str = "jobs_raw.txt") -> None:
    """Dump raw job data to file."""
    with open(filename, "a", encoding="utf-8") as file:
        for job in jobs:
            file.write(str(job) + "\n\n")


def main() -> None:
    """Main function to search for jobs and print details."""
    job_position = "C++ Developer"
    results = _search_jobs(job_position)

    if not results:
        print("No results found or error occurred")
        return

    print(results)
    # print(f"Found {len(jobs)} jobs")

    # _save_job_details_to_file(jobs)  # Save the first job details to file


if __name__ == "__main__":
    main()

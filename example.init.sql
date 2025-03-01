CREATE TABLE jobs (
    id SERIAL PRIMARY KEY, 
    company_name TEXT NOT NULL,
    position_title TEXT NOT NULL,
    application_date DATE,
    job_link TEXT,
    application_status TEXT,
    salary_range TEXT,
    contact_info TEXT,
    follow_up_notes_and_next_steps TEXT,
    -- Company-focused
    company_problem TEXT,
    value_proposition TEXT,
    company_priorities TEXT,
    required_skills TEXT
);
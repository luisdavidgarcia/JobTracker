CREATE TABLE jobs (
    id SERIAL PRIMARY KEY, 
    company_name TEXT NOT NULL,
    position_title TEXT NOT NULL,
    application_date DATE,
    application_status TEXT,
    job_link TEXT,
    application_method TEXT,
    salary_range TEXT,
    contact_info TEXT,
    follow_up_notes TEXT,
    next_steps TEXT,
    -- Company-focused
    company_problem TEXT,
    value_proposition TEXT,
    key_requirements TEXT,
    company_priorities TEXT,
    impact_metrics TEXT,
    -- Self-assessment
    required_skills TEXT,
    missing_skills TEXT,
    required_experience TEXT,
    project_alignment TEXT,
    skill_gap_action_plan TEXT
);
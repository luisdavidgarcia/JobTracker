CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    position_title TEXT NOT NULL,
    original_description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
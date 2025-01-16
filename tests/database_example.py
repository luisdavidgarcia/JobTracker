import os
import psycopg

DATABASE_URL = os.environ.get("DATABASE_URL")

try:
    conn = psycopg.connect(DATABASE_URL)
    with conn.cursor() as cur: # Using a context manager is recommended
        cur.execute("SELECT * FROM jobs;")
        result = cur.fetchone()
        print(f"Database connection successful: {result}")
    conn.commit()
except psycopg.OperationalError as e:
    print(f"Error connecting to the database: {e}")
except psycopg.Error as e:
    print(f"A database error occurred: {e}")
finally:
    if conn:
        conn.close()
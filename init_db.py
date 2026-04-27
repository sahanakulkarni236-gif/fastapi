import os
import psycopg2

def init_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT,
            address JSONB
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
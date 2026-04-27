import os
import psycopg2

def init_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    # Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT
        )
    """)

    # Addresses table (MISSING BEFORE → now fixed)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS addresses (
        id SERIAL PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
        street TEXT,
        city TEXT,
        state TEXT,
        zip TEXT
    )
""")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
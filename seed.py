import psycopg2
import random

conn = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="postgres",
    password="Mallsahi",
    port="5432"
)

cursor = conn.cursor()

cities = ["Bangalore", "Chennai", "Hyderabad", "Mumbai", "Delhi"]
states = ["KA", "TN", "TS", "MH", "DL"]

for i in range(1, 301):
    name = f"User{i}"
    email = f"user{i}@test.com"

    cursor.execute(
        "INSERT INTO customers (name, email) VALUES (%s, %s) RETURNING id",
        (name, email)
    )
    cid = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO addresses (customer_id, street, city, state, zip)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            cid,
            f"Street {i}",
            random.choice(cities),
            random.choice(states),
            f"{560000 + i}"
        )
    )

conn.commit()
cursor.close()
conn.close()

print("Inserted 300 customers")
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import psycopg2

from jose import JWTError, jwt
from datetime import datetime, timedelta

# ---------------- APP ----------------
app = FastAPI()

# ---------------- DB ----------------
conn = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="postgres",
    password="Mallsahi",
    port="5432"
)
cursor = conn.cursor()

# ---------------- JWT CONFIG ----------------
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

# ---------------- SECURITY (IMPORTANT FOR SWAGGER 🔒) ----------------
security = HTTPBearer()

# ---------------- TOKEN ----------------
def create_token(data: dict):
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.utcnow() + timedelta(hours=1)
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------------- MODELS ----------------
class Address(BaseModel):
    street: str
    city: str
    state: str
    zip: str


class Customer(BaseModel):
    name: str
    email: str
    address: Address


class LoginRequest(BaseModel):
    username: str
    password: str


# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: LoginRequest):
    if data.username == "admin" and data.password == "admin":
        token = create_token({"user": data.username})
        return {"access_token": token}

    raise HTTPException(status_code=401, detail="Invalid credentials")


# ---------------- CREATE CUSTOMER ----------------
@app.post("/customers", dependencies=[Depends(verify_token)])
def create_customer(customer: Customer):
    cursor.execute(
        "INSERT INTO customers (name, email) VALUES (%s, %s) RETURNING id",
        (customer.name, customer.email)
    )
    customer_id = cursor.fetchone()[0]

    cursor.execute(
        """
        INSERT INTO addresses (customer_id, street, city, state, zip)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            customer_id,
            customer.address.street,
            customer.address.city,
            customer.address.state,
            customer.address.zip
        )
    )

    conn.commit()
    return {"id": customer_id, "message": "Customer created"}


# ---------------- GET ALL ----------------
@app.get("/customers", dependencies=[Depends(verify_token)])
def get_all():
    cursor.execute("""
        SELECT c.id, c.name, c.email,
               a.street, a.city, a.state, a.zip
        FROM customers c
        JOIN addresses a ON c.id = a.customer_id
    """)
    rows = cursor.fetchall()

    return [
        {
            "id": r[0],
            "name": r[1],
            "email": r[2],
            "address": {
                "street": r[3],
                "city": r[4],
                "state": r[5],
                "zip": r[6]
            }
        }
        for r in rows
    ]


# ---------------- GET BY ID ----------------
@app.get("/customers/{id}", dependencies=[Depends(verify_token)])
def get_customer(id: int):
    cursor.execute("""
        SELECT c.id, c.name, c.email,
               a.street, a.city, a.state, a.zip
        FROM customers c
        JOIN addresses a ON c.id = a.customer_id
        WHERE c.id = %s
    """, (id,))

    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "address": {
            "street": row[3],
            "city": row[4],
            "state": row[5],
            "zip": row[6]
        }
    }


# ---------------- UPDATE ----------------
@app.put("/customers/{id}", dependencies=[Depends(verify_token)])
def update_customer(id: int, customer: Customer):
    cursor.execute(
        "UPDATE customers SET name=%s, email=%s WHERE id=%s",
        (customer.name, customer.email, id)
    )

    cursor.execute("""
        UPDATE addresses
        SET street=%s, city=%s, state=%s, zip=%s
        WHERE customer_id=%s
    """, (
        customer.address.street,
        customer.address.city,
        customer.address.state,
        customer.address.zip,
        id
    ))

    conn.commit()
    return {"message": "Updated successfully"}


# ---------------- DELETE ----------------
@app.delete("/customers/{id}", dependencies=[Depends(verify_token)])
def delete_customer(id: int):
    cursor.execute("DELETE FROM customers WHERE id=%s", (id,))
    conn.commit()
    return {"message": "Deleted successfully"}
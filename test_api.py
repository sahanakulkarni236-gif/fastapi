from fastapi.testclient import TestClient
from main import app  # change if your file name is different

client = TestClient(app)


def test_full_flow():
    # ----------------------------
    # 1. LOGIN
    # ----------------------------
    login = client.post(
        "/login",
        json={
            "username": "admin",
            "password": "admin"
        }
    )

    assert login.status_code == 200
    token = login.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # ----------------------------
    # 2. GET ALL CUSTOMERS
    # ----------------------------
    res = client.get("/customers", headers=headers)
    assert res.status_code == 200

    # ----------------------------
    # 3. CREATE CUSTOMER
    # ----------------------------
    res = client.post(
        "/customers",
        json={
            "name": "AI Test User",
            "email": "ai@test.com",
            "address": {
                "street": "123 Main St",
                "city": "Bangalore",
                "state": "KA",
                "zip": "560001"
            }
        },
        headers=headers
    )

    assert res.status_code in [200, 201]
    customer_id = res.json().get("id")

    # ----------------------------
    # 4. GET BY ID
    # ----------------------------
    res = client.get(f"/customers/{customer_id}", headers=headers)
    assert res.status_code == 200

    # ----------------------------
    # 5. UPDATE
    # ----------------------------
    res = client.put(
        f"/customers/{customer_id}",
        json={
            "name": "Updated User",
            "email": "updated@test.com",
            "address": {
                "street": "456 Updated St",
                "city": "Mysore",
                "state": "KA",
                "zip": "570001"
            }
        },
        headers=headers
    )

    assert res.status_code == 200

    # ----------------------------
    # 6. DELETE
    # ----------------------------
    res = client.delete(
        f"/customers/{customer_id}",
        headers=headers
    )

    assert res.status_code == 200
import httpx

BASE_URL = "http://127.0.0.1:8000"


def test_full_flow():
    # ----------------------------
    # 1. LOGIN
    # ----------------------------
    login = httpx.post(
        f"{BASE_URL}/login",
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
    res = httpx.get(
        f"{BASE_URL}/customers",
        headers=headers
    )

    assert res.status_code == 200

    # ----------------------------
    # 3. CREATE CUSTOMER (FIXED FOR YOUR PYDANTIC MODEL)
    # ----------------------------
    res = httpx.post(
        f"{BASE_URL}/customers",
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

    # Accept 200 or 201 depending on API behavior
    assert res.status_code in [200, 201]

    customer_id = res.json().get("id")

    # ----------------------------
    # 4. GET CUSTOMER BY ID
    # ----------------------------
    res = httpx.get(
        f"{BASE_URL}/customers/{customer_id}",
        headers=headers
    )

    assert res.status_code == 200

    # ----------------------------
    # 5. UPDATE CUSTOMER
    # ----------------------------
    res = httpx.put(
        f"{BASE_URL}/customers/{customer_id}",
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
    # 6. DELETE CUSTOMER
    # ----------------------------
    res = httpx.delete(
        f"{BASE_URL}/customers/{customer_id}",
        headers=headers
    )

    assert res.status_code == 200
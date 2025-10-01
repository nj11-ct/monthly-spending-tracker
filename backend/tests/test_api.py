from datetime import date

from app.core.utils import month_str


def test_create_and_list_transactions(client):
    r1 = client.post("/api/v1/transactions/", json={
        "date": "2025-09-30",
        "type": "income",
        "category": "salary",
        "amount": 5000.00,
        "description": "September salary"
    })
    assert r1.status_code == 201

    r2 = client.post("/api/v1/transactions/", json={
        "date": "2025-09-20",
        "type": "expense",
        "category": "groceries",
        "amount": 120.5,
        "description": "Weekly groceries"
    })
    assert r2.status_code == 201

    res = client.get("/api/v1/transactions", params={"month": "2025-09"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data[0]["date"] >= data[1]["date"]


def test_summary(client):
    # independent dataset per test via fresh DB in fixtures
    client.post("/api/v1/transactions/", json={
        "date": "2025-09-05",
        "type": "income",
        "category": "salary",
        "amount": 1000,
    })
    client.post("/api/v1/transactions/", json={
        "date": "2025-09-10",
        "type": "expense",
        "category": "eating_out",
        "amount": 200,
    })

    res = client.get("/api/v1/summary", params={"month": "2025-09"})
    assert res.status_code == 200
    s = res.json()
    assert s["income"] == 1000.0
    assert s["expenses"] == 200.0
    assert s["net"] == 800.0


def test_update_and_delete(client):
    create = client.post("/api/v1/transactions/", json={
        "date": "2025-09-12",
        "type": "expense",
        "category": "groceries",
        "amount": 10.0,
    })
    tx = create.json()

    upd = client.put(f"/api/v1/transactions/{tx['id']}", json={"amount": 15.25})
    assert upd.status_code == 200
    # response may serialize Decimal as string; cast for comparison
    assert float(upd.json()["amount"]) == 15.25

    dele = client.delete(f"/api/v1/transactions/{tx['id']}")
    assert dele.status_code == 204


def test_validation_errors(client):
    bad = client.post("/api/v1/transactions/", json={
        "date": "2025-09-01",
        "type": "invalid",
        "category": "salary",
        "amount": 5,
    })
    assert bad.status_code == 422

    bad_cat = client.post("/api/v1/transactions/", json={
        "date": "2025-09-01",
        "type": "income",
        "category": "invalid",
        "amount": 5,
    })
    assert bad_cat.status_code == 422

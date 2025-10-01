def test_dashboard_renders(client):
    # seed one tx
    client.post("/api/v1/transactions/", json={
        "date": "2025-09-30",
        "type": "income",
        "category": "salary",
        "amount": 5000.0,
    })

    res = client.get("/", params={"month": "2025-09"})
    assert res.status_code == 200
    html = res.text
    assert "September" in html or "2025-09" in html
    assert "Income" in html
    assert "Expenses" in html


def test_transactions_page_renders(client):
    client.post("/api/v1/transactions/", json={
        "date": "2025-09-15",
        "type": "expense",
        "category": "groceries",
        "amount": 12.25,
    })

    res = client.get("/transactions", params={"month": "2025-09"})
    assert res.status_code == 200
    html = res.text
    assert "Transactions" in html or "Income:" in html
    assert "groceries" in html or "Expenses:" in html


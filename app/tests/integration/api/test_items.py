"""Item API integration tests"""


def test_create_item(client):
    """Test creating an item"""
    response = client.post(
        "/api/v1/items/", json={"name": "Test Item", "price": 10.99, "is_offer": False}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["payload"]["name"] == "Test Item"


def test_get_item(client):
    """Test getting an item"""
    # First create an item
    create_response = client.post(
        "/api/v1/items/", json={"name": "Test Item", "price": 10.99, "is_offer": False}
    )
    item_id = create_response.json()["payload"]["id"]

    # Then get it
    response = client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["payload"]["id"] == item_id


def test_list_items(client):
    """Test listing items"""
    # Create a few items
    for i in range(3):
        client.post(
            "/api/v1/items/", json={"name": f"Item {i}", "price": 10.99 + i, "is_offer": False}
        )

    # List them
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["payload"]["items"]) >= 3

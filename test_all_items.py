#!/usr/bin/env python3
"""
Test script to verify all item endpoints work
"""

import asyncio
import sys
import traceback
from fastapi.testclient import TestClient

# Add the project root to the path so imports work
sys.path.insert(0, "/home/mohammad/Documents/Projects/Arcaan/Templates/fastapi_template")

from app.main import app


def test_all_item_endpoints():
    """Test all item endpoints"""
    client = TestClient(app)

    # Test GET /items/
    print("1. Testing GET /api/v1/items/ (list items)")
    response = client.get("/api/v1/items/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json() if response.content else 'No content'}")

    # Test POST /items/ (create item)
    print("\n2. Testing POST /api/v1/items/ (create item)")
    create_data = {"name": "Test Item", "price": 29.99, "is_offer": False}
    response = client.post("/api/v1/items/", json=create_data)
    print(f"   Status: {response.status_code}")
    result_data = response.json() if response.content else {}
    print(f"   Response: {result_data}")

    item_id = None
    if "payload" in result_data and "id" in result_data["payload"]:
        item_id = result_data["payload"]["id"]

    if item_id:
        # Test GET /items/{id} (get specific item)
        print(f"\n3. Testing GET /api/v1/items/{item_id} (get item)")
        response = client.get(f"/api/v1/items/{item_id}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json() if response.content else 'No content'}")

        # Test PUT /items/{id} (update item)
        print(f"\n4. Testing PUT /api/v1/items/{item_id} (update item)")
        update_data = {"name": "Updated Test Item", "price": 39.99, "is_offer": True}
        response = client.put(f"/api/v1/items/{item_id}", json=update_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json() if response.content else 'No content'}")

        # Test DELETE /items/{id} (delete item)
        print(f"\n5. Testing DELETE /api/v1/items/{item_id} (delete item)")
        response = client.delete(f"/api/v1/items/{item_id}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    else:
        print(f"\n3-5. Skipping individual item tests as no item was created")


if __name__ == "__main__":
    test_all_item_endpoints()

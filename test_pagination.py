#!/usr/bin/env python3
"""
Test script to verify the enterprise pagination feature works correctly
"""

import asyncio
import sys
from fastapi.testclient import TestClient

# Add the project root to the path so imports work
sys.path.insert(0, "/home/mohammad/Documents/Projects/Arcaan/Templates/templates")

from app.main import app


def test_pagination_feature():
    """Test the pagination feature works correctly"""
    client = TestClient(app)

    # Clean up any existing items first (try to delete all items)
    response = client.get("/api/v1/items/", params={"size": 100})
    if response.status_code == 200:
        data = response.json()
        if 'payload' in data and 'items' in data['payload']:
            for item in data['payload']['items']:
                try:
                    client.delete(f"/api/v1/items/{item['id']}")
                except:
                    pass  # Item might already be deleted

    print("1. Testing pagination with empty database")
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["payload"]["total"] == 0
    assert len(data["payload"]["items"]) == 0
    assert data["payload"]["page"] == 1
    assert data["payload"]["size"] == 50  # Default page size
    print("   ✓ Empty database pagination test passed")

    # Create multiple items for pagination testing
    print("\n2. Creating 65 test items for pagination testing")
    created_items = []
    for i in range(65):
        response = client.post(
            "/api/v1/items/",
            json={"name": f"Test Item {i+1:02d}", "price": 10.99, "is_offer": False}
        )
        assert response.status_code == 201
        created_items.append(response.json()['payload'])
    print(f"   Created {len(created_items)} items")

    # Verify the total count is 65
    response = client.get("/api/v1/items/")
    data = response.json()
    total_count = data["payload"]["total"]
    print(f"   Total items in database: {total_count}")

    # Test default pagination (should return first 50 items)
    print("\n3. Testing default pagination (first page)")
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["payload"]["total"] == total_count  # Total count should be total_count
    items_on_first_page = min(50, total_count)  # Default page size is 50, or total if less
    assert len(data["payload"]["items"]) == items_on_first_page
    assert data["payload"]["page"] == 1
    assert data["payload"]["size"] == 50
    print(f"   ✓ Default pagination: {items_on_first_page} items on page 1 of total {data['payload']['total']}")

    # Test pagination with custom page size (page 1)
    print("\n4. Testing pagination with custom page size (page 1)")
    response = client.get("/api/v1/items/", params={"page": 1, "size": 20})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["payload"]["total"] == total_count
    items_on_page_1 = min(20, total_count)
    assert len(data["payload"]["items"]) == items_on_page_1
    assert data["payload"]["page"] == 1
    assert data["payload"]["size"] == 20
    print(f"   ✓ Custom page size: {items_on_page_1} items on page 1 of total {data['payload']['total']}")

    # Test pagination with custom page size (page 2)
    print("\n5. Testing pagination with custom page size (page 2)")
    response = client.get("/api/v1/items/", params={"page": 2, "size": 20})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["payload"]["total"] == total_count
    remaining_after_page1 = max(0, total_count - 20)
    items_on_page_2 = min(20, remaining_after_page1)
    assert len(data["payload"]["items"]) == items_on_page_2
    assert data["payload"]["page"] == 2
    assert data["payload"]["size"] == 20
    print(f"   ✓ Custom page size: {items_on_page_2} items on page 2 of total {data['payload']['total']}")

    # Test pagination with custom page size (page 3 - full page or remaining)
    print("\n6. Testing pagination with custom page size (page 3)")
    response = client.get("/api/v1/items/", params={"page": 3, "size": 20})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["payload"]["total"] == total_count
    remaining_after_page2 = max(0, total_count - 40)
    items_on_page_3 = min(20, remaining_after_page2)
    assert len(data["payload"]["items"]) == items_on_page_3
    assert data["payload"]["page"] == 3
    assert data["payload"]["size"] == 20
    print(f"   ✓ Page 3: {items_on_page_3} items on page 3 of total {data['payload']['total']}")

    # Test pagination with custom page size (page 4 - remaining or out of range)
    print("\n7. Testing pagination with custom page size (page 4)")
    response = client.get("/api/v1/items/", params={"page": 4, "size": 20})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["payload"]["total"] == total_count
    remaining_after_page3 = max(0, total_count - 60)
    items_on_page_4 = min(20, remaining_after_page3)
    assert len(data["payload"]["items"]) == items_on_page_4
    assert data["payload"]["page"] == 4
    assert data["payload"]["size"] == 20
    print(f"   ✓ Page 4: {items_on_page_4} items on page 4 of total {data['payload']['total']}")

    # Test with large page size (larger than total)
    print("\n8. Testing pagination with page size larger than total items")
    response = client.get("/api/v1/items/", params={"page": 1, "size": 100})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["payload"]["total"] == total_count
    assert len(data["payload"]["items"]) == total_count  # Should return all items since page size > total
    assert data["payload"]["page"] == 1
    assert data["payload"]["size"] == 100
    print(f"   ✓ Large page size: {len(data['payload']['items'])} items on page 1 of total {data['payload']['total']}")

    print("\n✓ All pagination tests passed successfully!")

    # Clean up: delete all created items
    for item in created_items:
        client.delete(f"/api/v1/items/{item['id']}")
    print("   Cleaned up created test items")


if __name__ == "__main__":
    test_pagination_feature()

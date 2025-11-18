#!/usr/bin/env python3
"""
Debug script to test item endpoints and catch errors
"""

import asyncio
import sys
import traceback
from fastapi.testclient import TestClient

# Add the project root to the path so imports work
sys.path.insert(0, "/home/mohammad/Documents/Projects/Arcaan/Templates/fastapi_template")

from app.main import app


def test_items_endpoints():
    """Test the items endpoints to catch any exceptions"""
    client = TestClient(app)

    try:
        print("Testing GET /api/v1/items/ endpoint...")
        response = client.get("/api/v1/items/")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 500:
            print("Error occurred - this explains the Internal Server Error")
            print("Full response details:", response.json() if response.content else "No content")

    except Exception as e:
        print(f"Exception occurred while testing: {str(e)}")
        traceback.print_exc()

    # Test other endpoints as well
    try:
        print("\nTesting GET /api/v1/health/ endpoint...")
        response = client.get("/api/v1/health/")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception with health endpoint: {str(e)}")


if __name__ == "__main__":
    test_items_endpoints()

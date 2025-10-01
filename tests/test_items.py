from fastapi import status
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ping():
    r = client.get("/ping")
    assert r.status_code == status.HTTP_200_OK
    assert r.json() == {"status": "ok"}


def test_crud_flow():
    # create
    r = client.post("/items/", json={"name": "Pen", "description": "Blue ink"})
    assert r.status_code == status.HTTP_201_CREATED
    item = r.json()
    assert item["id"] > 0

    item_id = item["id"]

    # read
    r = client.get(f"/items/{item_id}")
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["name"] == "Pen"

    # update (put)
    r = client.put(f"/items/{item_id}", json={"description": "Black ink"})
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["description"] == "Black ink"

    # list
    r = client.get("/items")
    assert r.status_code == status.HTTP_200_OK
    assert any(i["id"] == item_id for i in r.json())

    # delete
    r = client.delete(f"/items/{item_id}")
    assert r.status_code == status.HTTP_204_NO_CONTENT

    # not found after delete
    r = client.get(f"/items/{item_id}")
    assert r.status_code == status.HTTP_404_NOT_FOUND

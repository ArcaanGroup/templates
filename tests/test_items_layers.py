import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core import deps
from app.repositories.items_repository import InMemoryItemsRepository
from app.services.items_service import ItemsService


@pytest.fixture()
def client():
    app = create_app()

    # fresh repo per test
    repo = InMemoryItemsRepository()

    def _get_repo_override():
        return repo

    def _get_service_override():
        return ItemsService(repo)

    app.dependency_overrides[deps.get_items_repo] = _get_repo_override
    app.dependency_overrides[deps.get_items_service] = _get_service_override

    return TestClient(app)


def test_ping(client: TestClient):
    r = client.get("/ping")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_crud_flow(client: TestClient):
    r = client.post("/items/", json={"name": "Pen", "description": "Blue"})
    assert r.status_code == 201
    item = r.json()
    iid = item["id"]

    r = client.get(f"/items/{iid}")
    assert r.status_code == 200

    r = client.put(f"/items/{iid}", json={"description": "Black"})
    assert r.status_code == 200
    assert r.json()["description"] == "Black"

    r = client.get("/items/")
    assert any(i["id"] == iid for i in r.json())

    r = client.delete(f"/items/{iid}")
    assert r.status_code == 204

    r = client.get(f"/items/{iid}")
    assert r.status_code == 404


def test_unique_name_rule(client: TestClient):
    client.post("/items/", json={"name": "Pen"})
    r = client.post("/items/", json={"name": "Pen"})
    assert r.status_code == 409

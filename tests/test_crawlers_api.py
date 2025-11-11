from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False}, future=True)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_crud_flow(client: TestClient) -> None:
    payload = {
        "name": "示例爬虫",
        "target_url": "https://example.com",
        "schedule": "0 0 * * *",
        "enabled": True,
        "notes": "每天抓取一次",
    }

    response = client.post("/api/crawlers", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == payload["name"]
    assert created["target_url"] == payload["target_url"]

    list_response = client.get("/api/crawlers")
    assert list_response.status_code == 200
    crawlers = list_response.json()
    assert len(crawlers) == 1

    crawler_id = created["id"]

    update_response = client.put(
        f"/api/crawlers/{crawler_id}",
        json={"notes": "立即执行", "enabled": False},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["notes"] == "立即执行"
    assert updated["enabled"] is False

    run_response = client.post(f"/api/crawlers/{crawler_id}/run")
    assert run_response.status_code == 200
    run_data = run_response.json()
    assert run_data["last_run_status"] == "success"
    assert run_data["last_run_at"] is not None

    delete_response = client.delete(f"/api/crawlers/{crawler_id}")
    assert delete_response.status_code == 204

    after_delete = client.get("/api/crawlers")
    assert after_delete.status_code == 200
    assert after_delete.json() == []


def test_duplicate_name(client: TestClient) -> None:
    payload = {
        "name": "重复名称",
        "target_url": "https://example.com",
    }
    first = client.post("/api/crawlers", json=payload)
    assert first.status_code == 201

    second = client.post("/api/crawlers", json=payload)
    assert second.status_code == 400
    assert "already exists" in second.json()["detail"]

import pytest
from fastapi import FastAPI, HTTPException
from starlette.testclient import TestClient

from devtrack_sdk.controller.devtrack_routes import router as devtrack_router
from devtrack_sdk.middleware.base import DevTrackMiddleware


@pytest.fixture
def app_with_middleware():
    app = FastAPI()
    app.include_router(devtrack_router)
    app.add_middleware(DevTrackMiddleware)

    @app.get("/")
    async def root():
        return {"message": "Hello"}

    @app.get("/error")
    def error_route():
        raise HTTPException(status_code=400, detail="Bad Request")

    @app.post("/users")
    async def create_user():
        return {"id": 1, "name": "Test User"}

    @app.get("/users/{user_id}/profile")
    async def user_profile(user_id: int):
        return {"user_id": user_id, "profile": "test"}

    return app


def test_root_logging(app_with_middleware):
    client = TestClient(app_with_middleware)
    DevTrackMiddleware.stats.clear()

    response = client.get("/")
    assert response.status_code == 200
    assert len(DevTrackMiddleware.stats) == 1
    log_entry = DevTrackMiddleware.stats[0]
    assert log_entry["path"] == "/"
    assert log_entry["method"] == "GET"
    assert "duration_ms" in log_entry
    assert "timestamp" in log_entry
    assert "client_ip" in log_entry
    assert log_entry["status_code"] == 200
    assert isinstance(log_entry["duration_ms"], int | float)
    assert isinstance(log_entry["timestamp"], str)
    assert isinstance(log_entry["client_ip"], str)


def test_error_logging(app_with_middleware):
    client = TestClient(app_with_middleware)
    DevTrackMiddleware.stats.clear()

    response = client.get("/error")
    assert response.status_code == 400
    assert len(DevTrackMiddleware.stats) == 1
    log_entry = DevTrackMiddleware.stats[0]
    assert log_entry["status_code"] == 400
    assert log_entry["path"] == "/error"
    assert "duration_ms" in log_entry
    assert "timestamp" in log_entry
    assert "client_ip" in log_entry
    assert isinstance(log_entry["duration_ms"], int | float)
    assert isinstance(log_entry["timestamp"], str)
    assert isinstance(log_entry["client_ip"], str)


def test_post_request_logging(app_with_middleware):
    client = TestClient(app_with_middleware)
    DevTrackMiddleware.stats.clear()

    response = client.post("/users", json={"name": "Test User"})
    assert response.status_code == 200
    assert len(DevTrackMiddleware.stats) == 1
    log_entry = DevTrackMiddleware.stats[0]
    assert log_entry["method"] == "POST"
    assert log_entry["path"] == "/users"
    assert "duration_ms" in log_entry
    assert "timestamp" in log_entry
    assert "client_ip" in log_entry
    assert log_entry["status_code"] == 200
    assert isinstance(log_entry["duration_ms"], int | float)
    assert isinstance(log_entry["timestamp"], str)
    assert isinstance(log_entry["client_ip"], str)


def test_internal_stats_endpoint(app_with_middleware):
    client = TestClient(app_with_middleware)
    DevTrackMiddleware.stats.clear()

    # Make multiple requests
    client.get("/")
    client.post("/users", json={"name": "Test User"})
    client.get("/error")

    response = client.get("/__devtrack__/stats")
    assert response.status_code == 200
    body = response.json()
    assert "total" in body
    assert body["total"] == 3
    assert "entries" in body
    assert isinstance(body["entries"], list)
    assert len(body["entries"]) == 3

    # Verify entries contain all required fields
    for entry in body["entries"]:
        assert "path" in entry
        assert "method" in entry
        assert "status_code" in entry
        assert "timestamp" in entry
        assert "duration_ms" in entry
        assert "client_ip" in entry
        assert isinstance(entry["duration_ms"], int | float)
        assert isinstance(entry["timestamp"], str)
        assert isinstance(entry["client_ip"], str)


def test_excluded_paths_not_logged(app_with_middleware):
    client = TestClient(app_with_middleware)
    DevTrackMiddleware.stats.clear()

    # These paths should be excluded from logging
    client.get("/docs")
    client.get("/redoc")
    client.get("/openapi.json")

    assert len(DevTrackMiddleware.stats) == 0

    # Test that a non-excluded path is logged
    client.get("/")
    assert len(DevTrackMiddleware.stats) == 1
    assert DevTrackMiddleware.stats[0]["path"] == "/"
    assert isinstance(DevTrackMiddleware.stats[0]["duration_ms"], int | float)
    assert isinstance(DevTrackMiddleware.stats[0]["timestamp"], str)
    assert isinstance(DevTrackMiddleware.stats[0]["client_ip"], str)


def test_path_pattern_normalization(app_with_middleware):
    client = TestClient(app_with_middleware)
    DevTrackMiddleware.stats.clear()

    # Test with a path that has parameters
    response = client.get("/users/123/profile")
    assert response.status_code == 200
    assert len(DevTrackMiddleware.stats) == 1
    log_entry = DevTrackMiddleware.stats[0]

    # Check both original path and normalized path pattern
    assert log_entry["path"] == "/users/123/profile"
    assert log_entry["path_pattern"] == "/users/{user_id}/profile"
    assert log_entry["path_params"] == {"user_id": "123"}

    # Test with a simple path
    response = client.get("/")
    assert response.status_code == 200
    assert len(DevTrackMiddleware.stats) == 2
    log_entry = DevTrackMiddleware.stats[1]

    # Simple paths should have the same path and pattern
    assert log_entry["path"] == "/"
    assert log_entry["path_pattern"] == "/"
    assert log_entry["path_params"] == {}


def test_middleware_logging(app_with_middleware):
    client = TestClient(app_with_middleware)
    DevTrackMiddleware.stats.clear()

    # Test successful request
    response = client.get("/")
    assert response.status_code == 200
    assert len(DevTrackMiddleware.stats) == 1
    assert DevTrackMiddleware.stats[0]["status_code"] == 200
    assert DevTrackMiddleware.stats[0]["method"] == "GET"
    assert DevTrackMiddleware.stats[0]["path"] == "/"
    assert DevTrackMiddleware.stats[0]["path_pattern"] == "/"
    assert DevTrackMiddleware.stats[0]["path_params"] == {}
    assert DevTrackMiddleware.stats[0]["duration_ms"] > 0
    assert isinstance(DevTrackMiddleware.stats[0]["timestamp"], str)
    assert isinstance(DevTrackMiddleware.stats[0]["client_ip"], str)

    # Test error request
    response = client.get("/error")
    assert response.status_code == 400
    assert len(DevTrackMiddleware.stats) == 2
    assert DevTrackMiddleware.stats[1]["status_code"] == 400
    assert DevTrackMiddleware.stats[1]["method"] == "GET"
    assert DevTrackMiddleware.stats[1]["path"] == "/error"
    assert DevTrackMiddleware.stats[1]["path_pattern"] == "/error"
    assert DevTrackMiddleware.stats[1]["path_params"] == {}
    assert DevTrackMiddleware.stats[1]["duration_ms"] > 0
    assert isinstance(DevTrackMiddleware.stats[1]["timestamp"], str)
    assert isinstance(DevTrackMiddleware.stats[1]["client_ip"], str)

    # Test POST request
    response = client.post("/users")
    assert response.status_code == 200
    assert len(DevTrackMiddleware.stats) == 3
    assert DevTrackMiddleware.stats[2]["status_code"] == 200
    assert DevTrackMiddleware.stats[2]["method"] == "POST"
    assert DevTrackMiddleware.stats[2]["path"] == "/users"
    assert DevTrackMiddleware.stats[2]["path_pattern"] == "/users"
    assert DevTrackMiddleware.stats[2]["path_params"] == {}
    assert DevTrackMiddleware.stats[2]["duration_ms"] > 0
    assert isinstance(DevTrackMiddleware.stats[2]["timestamp"], str)
    assert isinstance(DevTrackMiddleware.stats[2]["client_ip"], str)

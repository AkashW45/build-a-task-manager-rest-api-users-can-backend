import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.main import app, lifespan


@pytest.fixture
def client():
    """Provide a TestClient that triggers the lifespan."""
    with TestClient(app) as c:
        yield c


class TestRootEndpoint:
    """Tests for the root '/' endpoint."""

    def test_root_returns_200_and_message(self, client):
        """Happy path: GET / returns the expected message and 200 status."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {
            "message": "Task Manager API is running. See /docs for documentation."
        }

    def test_root_method_not_allowed(self, client):
        """Error path: POST to / returns 405 Method Not Allowed."""
        response = client.post("/")
        assert response.status_code == 405


class TestDocsEndpoint:
    """Edge case: documentation endpoints are reachable."""

    def test_docs_page_returns_200(self, client):
        """GET /docs returns the Swagger UI HTML."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
class TestLifespan:
    """Unit tests for the lifespan context manager."""

    @patch("app.main.Base")
    @patch("app.main.engine")
    async def test_lifespan_creates_tables(self, mock_engine, mock_base):
        """Lifespan should call Base.metadata.create_all on startup."""
        # Setup mock async context manager for engine.begin()
        mock_conn = AsyncMock()
        mock_conn.run_sync = AsyncMock()
        
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn

        # Call lifespan
        async with lifespan(app) as _:
            pass

        # Assert that create_all was called via run_sync
        mock_engine.begin.assert_awaited_once()
        mock_conn.run_sync.assert_called_once_with(mock_base.metadata.create_all)
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI

from app.database import get_db
from app.router import router
from app.schemas import TaskResponse


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


@pytest.fixture
async def async_client(app):
    async def override_get_db():
        yield AsyncMock()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_task(async_client):
    task_id = uuid.uuid4()
    task_data = TaskResponse(
        id=task_id,
        title="Test task",
        description="A description",
        due_date=datetime.now(timezone.utc),
        status="pending",
    )
    with patch("app.router.crud.create_task", new=AsyncMock(return_value=task_data)):
        response = await async_client.post(
            "/tasks/",
            json={
                "title": "Test task",
                "description": "A description",
                "due_date": task_data.due_date.isoformat(),
                "status": "pending",
            },
        )
    assert response.status_code == 201
    assert response.json()["id"] == str(task_id)


@pytest.mark.asyncio
async def test_list_tasks_pagination(async_client):
    tasks = [
        TaskResponse(
            id=uuid.uuid4(),
            title=f"Task {i}",
            due_date=datetime.now(timezone.utc),
            status="pending",
        )
        for i in range(2)
    ]
    mock_get_tasks = AsyncMock(return_value=tasks)
    with patch("app.router.crud.get_tasks", mock_get_tasks):
        response = await async_client.get("/tasks/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    mock_get_tasks.assert_called_once()
    call_args, call_kwargs = mock_get_tasks.call_args
    assert call_kwargs["skip"] == 0
    assert call_kwargs["limit"] == 2


@pytest.mark.asyncio
async def test_get_task_not_found(async_client):
    task_id = uuid.uuid4()
    mock_get_task = AsyncMock(return_value=None)
    with patch("app.router.crud.get_task", mock_get_task):
        response = await async_client.get(f"/tasks/{task_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


@pytest.mark.asyncio
async def test_update_task(async_client):
    task_id = uuid.uuid4()
    updated_task = TaskResponse(
        id=task_id,
        title="Updated title",
        description="Updated desc",
        due_date=datetime.now(timezone.utc),
        status="done",
    )
    mock_update = AsyncMock(return_value=updated_task)
    with patch("app.router.crud.update_task", mock_update):
        response = await async_client.put(
            f"/tasks/{task_id}",
            json={"title": "Updated title", "status": "done"},
        )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"


@pytest.mark.asyncio
async def test_delete_task_not_found(async_client):
    task_id = uuid.uuid4()
    mock_delete = AsyncMock(return_value=False)
    with patch("app.router.crud.delete_task", mock_delete):
        response = await async_client.delete(f"/tasks/{task_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}
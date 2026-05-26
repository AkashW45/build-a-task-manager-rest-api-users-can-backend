import pytest
from pydantic import ValidationError
from datetime import date, datetime, timedelta
from uuid import uuid4

from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.models import TaskStatus


def test_task_create_valid():
    data = {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "due_date": date.today() + timedelta(days=2),
        "status": TaskStatus.pending,
    }
    task = TaskCreate(**data)
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.due_date == date.today() + timedelta(days=2)
    assert task.status == TaskStatus.pending


def test_task_create_minimal_fields():
    # Only required title, everything else default.
    task = TaskCreate(title="Minimal")
    assert task.title == "Minimal"
    assert task.description is None
    assert task.due_date is None
    assert task.status == TaskStatus.pending


def test_task_create_empty_title_raises():
    with pytest.raises(ValidationError) as excinfo:
        TaskCreate(title="")
    assert "title" in str(excinfo.value)
    # Ensure error mentions length constraint
    assert "at least 1 characters" in str(excinfo.value)


def test_task_create_title_too_long_raises():
    long_title = "x" * 256
    with pytest.raises(ValidationError) as excinfo:
        TaskCreate(title=long_title)
    assert "at most 255 characters" in str(excinfo.value)


def test_task_create_description_too_long_raises():
    long_desc = "y" * 1001
    with pytest.raises(ValidationError) as excinfo:
        TaskCreate(title="Valid", description=long_desc)
    assert "at most 1000 characters" in str(excinfo.value)


def test_task_update_valid_partial():
    # Only update due_date
    update = TaskUpdate(due_date=date(2025, 12, 25))
    assert update.title is None
    assert update.description is None
    assert update.due_date == date(2025, 12, 25)
    assert update.status is None


def test_task_response_from_dict():
    task_id = uuid4()
    now = datetime.utcnow()
    data = {
        "id": task_id,
        "title": "Test task",
        "description": "A description",
        "due_date": date(2025, 12, 31),
        "status": TaskStatus.done,
        "created_at": now,
        "updated_at": now,
    }
    resp = TaskResponse(**data)
    assert resp.id == task_id
    assert resp.title == "Test task"
    assert resp.status == TaskStatus.done
    assert isinstance(resp.created_at, datetime)
    assert isinstance(resp.updated_at, datetime)
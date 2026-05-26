import uuid
import pytest
from datetime import date
from app.models import Task, TaskStatus

def test_task_status_enum_values():
    assert TaskStatus.pending.value == "pending"
    assert TaskStatus.done.value == "done"
    assert len(TaskStatus) == 2

def test_task_creation_happy_path():
    task_id = uuid.uuid4()
    title = "Build REST API"
    description = "Implement task manager REST API"
    due = date(2025, 12, 31)
    status = TaskStatus.pending
    task = Task(
        id=task_id,
        title=title,
        description=description,
        due_date=due,
        status=status
    )
    assert task.id == task_id
    assert task.title == title
    assert task.description == description
    assert task.due_date == due
    assert task.status == status
    assert task.created_at is None   # handled by server_default
    assert task.updated_at is None   # handled by server_default

def test_task_defaults():
    task = Task(title="Minimal task")
    assert task.title == "Minimal task"
    assert task.description == ""
    assert task.status == TaskStatus.pending
    assert task.due_date is None
    assert task.id is None   # default callable only triggered on insert

def test_task_repr():
    task_id = uuid.uuid4()
    task = Task(id=task_id, title="Test", status=TaskStatus.done)
    repr_str = repr(task)
    assert "<Task(id=" in repr_str
    assert f"id={task_id}" in repr_str
    assert "title=Test" in repr_str
    assert "status=TaskStatus.done" in repr_str

def test_title_column_not_nullable():
    title_col = Task.__table__.columns["title"]
    assert title_col.nullable is False

def test_id_is_uuid_default():
    id_col = Task.__table__.columns["id"]
    assert id_col.default.arg == uuid.uuid4
import pytest
from pydantic import ValidationError
from datetime import date, datetime
from uuid import uuid4
from app.schemas import TaskCreate, TaskUpdate, TaskResponse


class TestTaskCreatePriority:
    """Tests for TaskCreate priority field."""

    def test_create_with_default_priority(self):
        """Default priority should be 'medium' when not provided."""
        data = {"title": "My Task"}
        task = TaskCreate(**data)
        assert task.priority == "medium"

    @pytest.mark.parametrize("priority", ["low", "medium", "high"])
    def test_create_with_valid_priority(self, priority):
        """All three literal priorities should be accepted."""
        data = {"title": "Task", "priority": priority}
        task = TaskCreate(**data)
        assert task.priority == priority

    @pytest.mark.parametrize("invalid_priority", ["urgent", "", "HIGH", " medium ", "low "])
    def test_create_with_invalid_priority_raises_validation_error(self, invalid_priority):
        """Non-literal values raise ValidationError."""
        data = {"title": "Task", "priority": invalid_priority}
        with pytest.raises(ValidationError):
            TaskCreate(**data)

    def test_create_missing_title_raises_validation_error(self):
        """Missing required title field raises ValidationError."""
        data = {"priority": "high"}
        with pytest.raises(ValidationError):
            TaskCreate(**data)


class TestTaskUpdatePriority:
    """Tests for TaskUpdate optional priority field."""

    def test_update_with_priority_none_is_valid(self):
        """Explicit None priority should be accepted and remain None."""
        update = TaskUpdate(priority=None)
        assert update.priority is None

    def test_update_omit_priority_is_none(self):
        """Omitting the priority field should result in None."""
        update = TaskUpdate(title="New Title")
        assert update.priority is None


class TestTaskResponsePriority:
    """Tests for TaskResponse priority field (string, not validated)."""

    def test_response_accepts_any_string(self):
        """TaskResponse.priority is a plain str, accepts any value without validation."""
        task_id = uuid4()
        now = datetime.now()
        response = TaskResponse(
            id=task_id,
            title="Task",
            description=None,
            due_date=None,
            status="pending",
            priority="urgent",           # Not restricted to low/medium/high
            created_at=now,
            updated_at=now
        )
        assert response.priority == "urgent"
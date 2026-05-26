import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.crud import create_task, get_task, get_tasks, update_task, delete_task, get_tasks_by_priority
from app.schemas import TaskCreate, TaskUpdate


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def sample_task_data():
    return {"title": "Test", "description": "Desc", "due_date": "2025-01-01", "status": "pending", "priority": "medium"}


@pytest.fixture
def task_create_in(sample_task_data):
    return TaskCreate(**sample_task_data)


@pytest.fixture
def task_update_in():
    return TaskUpdate(title="Updated Title")


@pytest.fixture
def mock_task_instance(sample_task_data):
    task = MagicMock()
    for k, v in sample_task_data.items():
        setattr(task, k, v)
    task.id = uuid4()
    return task


@patch("app.crud.Task")
@pytest.mark.asyncio
async def test_create_task_happy_path(mock_task_cls, mock_db, task_create_in, sample_task_data):
    # Given
    mock_task_cls.return_value = mock_task_instance = MagicMock()
    for k, v in sample_task_data.items():
        setattr(mock_task_instance, k, v)

    # When
    result = await create_task(mock_db, task_create_in)

    # Then
    mock_task_cls.assert_called_once_with(**sample_task_data)
    mock_db.add.assert_called_once_with(mock_task_instance)
    mock_db.flush.assert_awaited_once()
    mock_db.refresh.assert_awaited_once_with(mock_task_instance)
    assert result is mock_task_instance


@patch("app.crud.Task")
@patch("app.crud.select")
@pytest.mark.asyncio
@pytest.mark.parametrize("found", [True, False], ids=["found", "not_found"])
async def test_get_task(mock_select, mock_task_cls, mock_db, found):
    task_id = uuid4()
    mock_stmt = MagicMock()
    mock_select.return_value = mock_stmt
    mock_select.return_value.where.return_value = mock_stmt

    if found:
        expected_task = MagicMock()
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = expected_task
    else:
        expected_task = None
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None

    mock_db.execute.return_value = mock_result

    result = await get_task(mock_db, task_id)

    mock_select.assert_called_once_with(mock_task_cls)
    mock_stmt.where.assert_called_once()
    mock_db.execute.assert_awaited_once_with(mock_stmt)
    assert result is expected_task


@patch("app.crud.Task")
@patch("app.crud.select")
@pytest.mark.asyncio
async def test_get_tasks_with_pagination(mock_select, mock_task_cls, mock_db):
    mock_stmt = MagicMock()
    mock_select.return_value = mock_stmt
    mock_stmt.offset.return_value = mock_stmt
    mock_stmt.limit.return_value = mock_stmt
    mock_stmt.order_by.return_value = mock_stmt

    tasks = [MagicMock(), MagicMock()]
    mock_result = AsyncMock()
    mock_result.scalars.return_value.all.return_value = tasks
    mock_db.execute.return_value = mock_result

    result = await get_tasks(mock_db, skip=10, limit=2)

    mock_select.assert_called_once_with(mock_task_cls)
    mock_stmt.offset.assert_called_once_with(10)
    mock_stmt.limit.assert_called_once_with(2)
    mock_stmt.order_by.assert_called_once()
    mock_db.execute.assert_awaited_once_with(mock_stmt)
    assert result == tasks


@patch("app.crud.Task")
@patch("app.crud.select")
@pytest.mark.asyncio
async def test_get_tasks_empty(mock_select, mock_task_cls, mock_db):
    mock_stmt = MagicMock()
    mock_select.return_value = mock_stmt
    mock_stmt.offset.return_value = mock_stmt
    mock_stmt.limit.return_value = mock_stmt
    mock_stmt.order_by.return_value = mock_stmt

    mock_result = AsyncMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    result = await get_tasks(mock_db, skip=0, limit=10)
    assert result == []


@patch("app.crud.get_task")
@pytest.mark.asyncio
@pytest.mark.parametrize("task_exists", [True, False], ids=["task_found", "task_not_found"])
async def test_update_task(mock_get_task, mock_db, task_update_in, task_exists):
    task_id = uuid4()
    if task_exists:
        existing_task = MagicMock()
        mock_get_task.return_value = existing_task
    else:
        existing_task = None
        mock_get_task.return_value = None

    result = await update_task(mock_db, task_id, task_update_in)

    mock_get_task.assert_awaited_once_with(mock_db, task_id)
    if task_exists:
        assert result is existing_task
        assert existing_task.title == "Updated Title"
        mock_db.flush.assert_awaited_once()
        mock_db.refresh.assert_awaited_once_with(existing_task)
    else:
        assert result is None
        mock_db.flush.assert_not_awaited()
        mock_db.refresh.assert_not_awaited()


@patch("app.crud.Task")
@patch("app.crud.delete")
@pytest.mark.asyncio
@pytest.mark.parametrize("deleted", [True, False], ids=["delete_found", "delete_not_found"])
async def test_delete_task(mock_delete_func, mock_task_cls, mock_db, deleted):
    task_id = uuid4()
    mock_stmt = MagicMock()
    mock_delete_func.return_value = mock_stmt
    mock_stmt.where.return_value = mock_stmt
    mock_stmt.returning.return_value = mock_stmt

    mock_result = AsyncMock()
    if deleted:
        mock_result.scalar.return_value = task_id
    else:
        mock_result.scalar.return_value = None
    mock_db.execute.return_value = mock_result

    result = await delete_task(mock_db, task_id)

    mock_delete_func.assert_called_once_with(mock_task_cls)
    mock_stmt.where.assert_called_once()
    mock_stmt.returning.assert_called_once_with(mock_task_cls.id)
    mock_db.execute.assert_awaited_once_with(mock_stmt)
    assert result == deleted
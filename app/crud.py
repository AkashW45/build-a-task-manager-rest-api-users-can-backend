from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task
from app.schemas import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, task_in: TaskCreate) -> Task:
    """Create a new task."""
    task = Task(**task_in.model_dump())
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: UUID) -> Task | None:
    """Get a single task by ID."""
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_tasks(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Task]:
    """Get a list of tasks with pagination."""
    stmt = select(Task).offset(skip).limit(limit).order_by(Task.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_task(db: AsyncSession, task_id: UUID, task_in: TaskUpdate) -> Task | None:
    """Update an existing task. Returns None if not found."""
    task = await get_task(db, task_id)
    if not task:
        return None
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    await db.flush()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: UUID) -> bool:
    """Delete a task by ID. Returns True if deleted, False if not found."""
    stmt = delete(Task).where(Task.id == task_id).returning(Task.id)
    result = await db.execute(stmt)
    return result.scalar() is not None

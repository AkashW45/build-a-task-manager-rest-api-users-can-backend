from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import crud
from app.schemas import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_endpoint(task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create a new task."""
    task = await crud.create_task(db, task_in)
    return task


@router.get("/", response_model=list[TaskResponse])
async def list_tasks_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Get all tasks with pagination."""
    tasks = await crud.get_tasks(db, skip=skip, limit=limit)
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_endpoint(task_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single task by ID."""
    task = await crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(task_id: UUID, task_in: TaskUpdate, db: AsyncSession = Depends(get_db)):
    """Update an existing task."""
    task = await crud.update_task(db, task_id, task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_endpoint(task_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a task."""
    deleted = await crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return None

from pydantic import BaseModel, Field
from datetime import date, datetime
from uuid import UUID
from typing import Optional
from app.models import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[date] = None
    status: TaskStatus = TaskStatus.pending


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[date] = None
    status: Optional[TaskStatus] = None


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    due_date: Optional[date]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

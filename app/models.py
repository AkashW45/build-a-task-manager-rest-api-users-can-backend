import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Date, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base

import enum


class TaskStatus(str, enum.Enum):
    pending = "pending"
    done = "done"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True, default="")
    due_date = Column(Date, nullable=True)
    status = Column(Enum(TaskStatus, name="task_status"), nullable=False, default=TaskStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"

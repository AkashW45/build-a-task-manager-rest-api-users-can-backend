import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from app.models import Task, TaskStatus
from app.database import Base

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_create_task_with_explicit_priority(db_session):
    task = Task(
        title="Buy milk",
        description="Need milk",
        priority="high"
    )
    db_session.add(task)
    db_session.flush()

    assert task.priority == "high"
    assert task.id is not None

def test_default_priority_is_medium(db_session):
    task = Task(title="Default priority task")
    db_session.add(task)
    db_session.flush()

    assert task.priority == "medium"

def test_invalid_priority_raises_integrity_error(db_session):
    task = Task(
        title="Invalid priority",
        priority="urgent"
    )
    db_session.add(task)
    with pytest.raises(IntegrityError):
        db_session.flush()

def test_case_sensitive_priority_considered_invalid(db_session):
    task = Task(
        title="Case sensitive",
        priority="Low"
    )
    db_session.add(task)
    with pytest.raises(IntegrityError):
        db_session.flush()

def test_task_repr(db_session):
    task = Task(
        title="Repr test",
        description="desc",
        priority="medium",
        status=TaskStatus.done
    )
    db_session.add(task)
    db_session.flush()
    expected_repr = f"<Task(id={task.id}, title=Repr test, status=TaskStatus.done, priority=medium)>"
    assert repr(task) == expected_repr
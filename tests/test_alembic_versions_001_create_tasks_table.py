import importlib.util
import os
import pytest
from unittest.mock import patch, ANY
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

@pytest.fixture(scope="session")
def migration_module():
    migration_path = os.path.join(os.path.dirname(__file__), '..', 'alembic', 'versions', '001_create_tasks_table.py')
    spec = importlib.util.spec_from_file_location("migration", migration_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_upgrade_creates_table_correctly(migration_module):
    with patch('alembic.op.create_table') as mock_create_table, \
         patch('alembic.op.create_index') as mock_create_index, \
         patch('alembic.op.f', side_effect=lambda x: x):
        migration_module.upgrade()

        # assert table creation
        mock_create_table.assert_called_once()
        args, _ = mock_create_table.call_args
        assert args[0] == 'tasks'
        columns = args[1:]
        assert len(columns) == 7  # id, title, description, due_date, status, created_at, updated_at

        # check id column
        id_col = next((c for c in columns if c.name == 'id'), None)
        assert id_col is not None
        assert id_col.primary_key
        assert isinstance(id_col.type, postgresql.UUID)
        assert id_col.type.as_uuid is True
        assert str(id_col.server_default.arg) == 'gen_random_uuid()'

        # check title column
        title_col = next((c for c in columns if c.name == 'title'), None)
        assert title_col is not None
        assert isinstance(title_col.type, sa.String)
        assert title_col.type.length == 255
        assert title_col.nullable is False

        # check status column (Enum with correct name and values)
        status_col = next((c for c in columns if c.name == 'status'), None)
        assert status_col is not None
        assert isinstance(status_col.type, sa.Enum)
        assert status_col.type.enums == ('pending', 'done')
        assert status_col.type.name == 'task_status'
        assert status_col.nullable is False
        assert str(status_col.server_default.arg) == 'pending'

        # check timestamps
        created_col = next((c for c in columns if c.name == 'created_at'), None)
        assert created_col is not None
        assert created_col.server_default.arg == sa.func.now()
        updated_col = next((c for c in columns if c.name == 'updated_at'), None)
        assert updated_col is not None
        assert updated_col.server_default.arg == sa.func.now()

        # assert index creation
        mock_create_index.assert_called_once_with('ix_tasks_id', 'tasks', ['id'])

def test_downgrade_removes_all_objects(migration_module):
    with patch('alembic.op.drop_index') as mock_drop_index, \
         patch('alembic.op.drop_table') as mock_drop_table, \
         patch('alembic.op.execute') as mock_execute, \
         patch('alembic.op.f', side_effect=lambda x: x):
        migration_module.downgrade()

        mock_drop_index.assert_called_once_with('ix_tasks_id', table_name='tasks')
        mock_drop_table.assert_called_once_with('tasks')
        mock_execute.assert_called_once_with('DROP TYPE IF EXISTS task_status')

def test_task_status_enum_properties():
    # Verify the enum used in the migration is defined with the expected name and values
    from alembic.versions.001_create_tasks_table import upgrade
    with patch('alembic.op.create_table') as mock_create_table, \
         patch('alembic.op.create_index'), \
         patch('alembic.op.f', side_effect=lambda x: x):
        upgrade()
        columns = mock_create_table.call_args[0][1:]
        status_col = next((c for c in columns if c.name == 'status'), None)
        assert status_col is not None
        enum_type = status_col.type
        assert isinstance(enum_type, sa.Enum)
        assert enum_type.name == 'task_status'
        assert set(enum_type.enums) == {'pending', 'done'}

def test_upgrade_raises_on_create_table_failure(migration_module):
    with patch('alembic.op.create_table', side_effect=Exception("Table exists")), \
         patch('alembic.op.create_index'), \
         patch('alembic.op.f', side_effect=lambda x: x):
        with pytest.raises(Exception, match="Table exists"):
            migration_module.upgrade()
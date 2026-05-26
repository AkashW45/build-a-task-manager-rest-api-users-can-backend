import asyncio
import sys
from unittest.mock import patch, MagicMock, AsyncMock, call

import pytest

# NOTE: We avoid importing alembic.env at module level because its top-level code
# executes run_migrations_offline() or run_migrations_online() immediately.
# Each test patches the required names before importing the functions or module.


@pytest.fixture
def mock_alembic_config():
    """Provide a mock alembic config object."""
    mock = MagicMock()
    mock.get_main_option.return_value = "sqlite:///:memory:"
    # Simulate config_ini_section and get_section for async branch
    mock.config_ini_section = "alembic"
    mock.get_section.return_value = {"sqlalchemy.url": "sqlite+aiosqlite:///:memory:"}
    return mock


@pytest.fixture
def mock_alembic_context():
    """Provide a mock alembic context object."""
    mock = MagicMock()
    mock.configure = MagicMock()
    mock.begin_transaction = MagicMock()
    mock.run_migrations = MagicMock()
    return mock


class TestRunMigrationsOffline:
    def test_happy_path(self, mock_alembic_config, mock_alembic_context):
        with patch("alembic.env.config", mock_alembic_config), patch(
            "alembic.env.context", mock_alembic_context
        ), patch("alembic.env.run_migrations_offline", side_effect=lambda: None), patch(
            "alembic.env.run_migrations_online", side_effect=lambda: None
        ):
            from alembic.env import run_migrations_offline, target_metadata

            run_migrations_offline()

            mock_alembic_config.get_main_option.assert_called_once_with(
                "sqlalchemy.url"
            )
            mock_alembic_context.configure.assert_called_once_with(
                url=mock_alembic_config.get_main_option.return_value,
                target_metadata=target_metadata,
                literal_binds=True,
                dialect_opts={"paramstyle": "named"},
            )
            mock_alembic_context.begin_transaction.assert_called_once()
            mock_alembic_context.run_migrations.assert_called_once()

    def test_url_missing_runs_without_error(self, mock_alembic_context):
        """Edge case: when config.get_main_option returns None."""
        mock_config = MagicMock()
        mock_config.get_main_option.return_value = None
        with patch("alembic.env.config", mock_config), patch(
            "alembic.env.context", mock_alembic_context
        ), patch("alembic.env.run_migrations_offline", side_effect=lambda: None), patch(
            "alembic.env.run_migrations_online", side_effect=lambda: None
        ):
            from alembic.env import run_migrations_offline, target_metadata

            # Should not raise
            run_migrations_offline()

            mock_alembic_context.configure.assert_called_once_with(
                url=None,
                target_metadata=target_metadata,
                literal_binds=True,
                dialect_opts={"paramstyle": "named"},
            )


class TestDoRunMigrations:
    def test_configure_and_run(self, mock_alembic_context):
        """do_run_migrations uses context from the module."""
        with patch("alembic.env.context", mock_alembic_context), patch(
            "alembic.env.run_migrations_offline", side_effect=lambda: None
        ), patch(
            "alembic.env.run_migrations_online", side_effect=lambda: None
        ):
            from alembic.env import do_run_migrations, target_metadata

            connection = MagicMock()
            do_run_migrations(connection)

            mock_alembic_context.configure.assert_called_once_with(
                connection=connection, target_metadata=target_metadata
            )
            mock_alembic_context.begin_transaction.assert_called_once()
            mock_alembic_context.run_migrations.assert_called_once()


class TestRunAsyncMigrations:
    def test_happy_path(self):
        """Simulate the full async migration without real I/O."""
        mock_connection = MagicMock()
        mock_connectable = MagicMock()
        mock_connectable.connect = AsyncMock(
            return_value=MagicMock(__aenter__=AsyncMock(return_value=mock_connection))
        )
        mock_connectable.dispose = AsyncMock()

        mock_config = MagicMock()
        mock_config.config_ini_section = "alembic"
        mock_config.get_section.return_value = {
            "sqlalchemy.url": "postgresql+asyncpg:///test"
        }

        with patch(
            "alembic.env.async_engine_from_config",
            return_value=mock_connectable,
        ) as mock_async_engine, patch("alembic.env.config", mock_config), patch(
            "alembic.env.run_migrations_offline", side_effect=lambda: None
        ), patch(
            "alembic.env.run_migrations_online", side_effect=lambda: None
        ):
            from alembic.env import run_async_migrations

            asyncio.run(run_async_migrations())

            mock_async_engine.assert_called_once_with(
                mock_config.get_section.return_value,
                prefix="sqlalchemy.",
                poolclass=pytest.importorskip("sqlalchemy.pool").NullPool,
            )
            mock_connectable.connect.assert_called_once()
            mock_connection.run_sync.assert_called_once()
            mock_connectable.dispose.assert_called_once()


class TestRunMigrationsOnline:
    def test_dispatches_to_async_run(self):
        """run_migrations_online delegates to asyncio.run(run_async_migrations())."""
        with patch("asyncio.run") as mock_asyncio_run, patch(
            "alembic.env.run_async_migrations"
        ) as mock_async_fn, patch(
            "alembic.env.run_migrations_offline", side_effect=lambda: None
        ), patch(
            "alembic.env.run_migrations_online", side_effect=lambda: None
        ):
            mock_async_fn.return_value = asyncio.sleep(0)  # a real coroutine object

            from alembic.env import run_migrations_online

            run_migrations_online()
            mock_async_fn.assert_called_once()
            mock_asyncio_run.assert_called_once_with(mock_async_fn.return_value)


class TestModuleTopLevelConditional:
    def test_offline_mode_calls_offline_migrations(self):
        """When context.is_offline_mode() is True, run_migrations_offline is called."""
        with patch("alembic.env.context.is_offline_mode", return_value=True), patch(
            "alembic.env.run_migrations_offline"
        ) as mock_offline, patch("alembic.env.run_migrations_online") as mock_online:
            # Ensure the module is freshly imported after patching
            sys.modules.pop("alembic.env", None)
            import alembic.env

            mock_offline.assert_called_once()
            mock_online.assert_not_called()

    def test_online_mode_calls_online_migrations(self):
        """When context.is_offline_mode() is False, run_migrations_online is called."""
        with patch("alembic.env.context.is_offline_mode", return_value=False), patch(
            "alembic.env.run_migrations_offline"
        ) as mock_offline, patch("alembic.env.run_migrations_online") as mock_online:
            sys.modules.pop("alembic.env", None)
            import alembic.env

            mock_offline.assert_not_called()
            mock_online.assert_called_once()
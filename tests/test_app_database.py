import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine, async_session_factory, Base, get_db


@pytest.mark.asyncio
async def test_engine_created_with_settings_database_url():
    """Test that create_async_engine is called with the correct URL and echo setting."""
    with patch("app.database.create_async_engine") as mock_create_engine:
        # Force re-import to trigger engine creation with mock in place
        import importlib
        import app.database
        importlib.reload(app.database)
        mock_create_engine.assert_called_once_with(
            app.database.settings.database_url, echo=False
        )


@pytest.mark.asyncio
async def test_get_db_happy_path_commits_and_closes():
    """On successful use, session is committed and closed."""
    session_mock = AsyncMock(spec=AsyncSession)
    session_mock.commit = AsyncMock()
    session_mock.rollback = AsyncMock()
    session_mock.close = AsyncMock()

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = session_mock

    mock_factory = AsyncMock(return_value=mock_ctx)
    with patch("app.database.async_session_factory", mock_factory):
        async for session in get_db():
            assert session is session_mock
            # Let the loop finish normally

    session_mock.commit.assert_awaited_once()
    session_mock.rollback.assert_not_awaited()
    session_mock.close.assert_awaited_once()
    mock_factory.assert_called_once_with()


@pytest.mark.asyncio
async def test_get_db_error_rollback_and_closes():
    """When an exception occurs during session use, rollback is called and session closed."""
    session_mock = AsyncMock(spec=AsyncSession)
    session_mock.commit = AsyncMock()
    session_mock.rollback = AsyncMock()
    session_mock.close = AsyncMock()

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = session_mock

    mock_factory = AsyncMock(return_value=mock_ctx)
    with patch("app.database.async_session_factory", mock_factory):
        with pytest.raises(ValueError):
            async for session in get_db():
                assert session is session_mock
                raise ValueError("Something went wrong")

    session_mock.rollback.assert_awaited_once()
    session_mock.commit.assert_not_awaited()
    session_mock.close.assert_awaited_once()
    mock_factory.assert_called_once_with()
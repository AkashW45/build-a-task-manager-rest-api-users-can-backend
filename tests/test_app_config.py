import pytest
from pydantic import ValidationError
from app.config import Settings


def test_settings_defaults():
    """Happy path: Settings instantiated with no env overrides uses default values."""
    settings = Settings()
    assert settings.database_url == "postgresql+asyncpg://taskuser:taskpass@localhost:5432/tasks"
    assert settings.app_host == "0.0.0.0"
    assert settings.app_port == 8000


def test_settings_override_database_url(monkeypatch):
    """Happy path: Environment variable overrides the default database_url."""
    new_url = "postgresql+asyncpg://test:test@testhost/testdb"
    monkeypatch.setenv("database_url", new_url)
    settings = Settings()
    assert settings.database_url == new_url


def test_settings_env_case_insensitive(monkeypatch):
    """Edge case: Environment variable with different case still maps to field."""
    new_url = "postgresql+asyncpg://case:insensitive@host/casedb"
    monkeypatch.setenv("DATABASE_URL", new_url)
    settings = Settings()
    assert settings.database_url == new_url


def test_settings_app_port_int_conversion(monkeypatch):
    """Edge case: APP_PORT string from env is correctly parsed as int."""
    monkeypatch.setenv("APP_PORT", "9090")
    settings = Settings()
    assert settings.app_port == 9090
    assert isinstance(settings.app_port, int)


def test_settings_missing_env_file():
    """Edge case: Missing .env file does not cause instantiation failure."""
    # Simply instantiating Settings without a .env file should succeed
    try:
        settings = Settings()
    except Exception as e:
        pytest.fail(f"Instantiation raised an unexpected exception: {e}")


def test_settings_invalid_port_type_raises_error(monkeypatch):
    """Error path: Setting APP_PORT to a non-integer string raises ValidationError."""
    monkeypatch.setenv("APP_PORT", "not_a_number")
    with pytest.raises(ValidationError):
        Settings()
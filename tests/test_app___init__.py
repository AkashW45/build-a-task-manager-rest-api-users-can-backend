import pytest
import app

def test_app_package_imports_successfully():
    """Happy path: app package should import and be recognized as a package."""
    assert hasattr(app, '__path__')
    assert app.__name__ == 'app'

def test_app_package_has_no_explicit_exports():
    """Edge case: empty __init__ should not expose any custom attributes."""
    for attr_name in dir(app):
        if not attr_name.startswith('__'):
            pytest.fail(f"Unexpected non-dunder attribute '{attr_name}' found in app package")

def test_importing_nonexistent_submodule_raises_import_error():
    """Error path: trying to import a missing submodule raises ImportError."""
    with pytest.raises(ImportError):
        from app import nonexistent_submodule
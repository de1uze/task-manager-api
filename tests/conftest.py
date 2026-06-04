import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import TaskStore
import app.store as store_module
import app.main as main_module


@pytest.fixture(autouse=True)
def fresh_store():
    """Each test gets an empty in-memory store."""
    new_store = TaskStore()
    store_module.store = new_store
    main_module.store = new_store
    yield new_store


@pytest.fixture
def client():
    return TestClient(app)

import pytest
from app.repository import OrderRepository


@pytest.fixture(autouse=True, scope="function")
def clear_repository():
    """
    Automatically clear the repository before each test.
    """
    repo = OrderRepository()
    repo.clear_storage()
    yield
    # Cleanup after test
    repo.clear_storage()

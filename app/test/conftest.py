import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():  # Arrange (organização)
    return TestClient(app)


# client = TestClient(app)

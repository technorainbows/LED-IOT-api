"""Configuration file for pytest."""

import pytest
from main import server



@pytest.fixture
def app():
    """Create a fixture whose name is "app" and returns our flask server instance."""
    app = server.app
    return app

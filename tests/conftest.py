"""
Pytest configuration and shared fixtures.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient


@pytest.fixture
def mock_telegram_client():
    """Mock Telegram client for testing without API calls."""
    client = MagicMock()
    client.send_message = AsyncMock(return_value={"ok": True, "result": {"message_id": 123}})
    client.edit_message_text = AsyncMock(return_value={"ok": True})
    client.get_me = AsyncMock(return_value={"ok": True, "result": {"username": "test_bot"}})
    client.close = AsyncMock()
    return client


@pytest.fixture
def sample_telegram_update():
    """Sample Telegram webhook update."""
    return {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "date": 1706800000,
            "chat": {
                "id": 123456789,
                "type": "private",
                "first_name": "Test",
                "username": "testuser"
            },
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "text": "/test"
        }
    }


@pytest.fixture
def sample_command_update():
    """Sample command update for testing."""
    def _make_update(command: str, args: str = ""):
        text = f"{command} {args}".strip() if args else command
        return {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "date": 1706800000,
                "chat": {"id": 123456789, "type": "private"},
                "from": {"id": 123456789, "is_bot": False, "first_name": "Test"},
                "text": text
            }
        }
    return _make_update

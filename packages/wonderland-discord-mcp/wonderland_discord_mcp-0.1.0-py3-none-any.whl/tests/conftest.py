import pytest
import os
from unittest.mock import patch
from main import DiscordMCPServer


@pytest.fixture
def mock_discord_token():
    """Mock Discord token for testing"""
    return "test_token_123456789"


@pytest.fixture
def discord_server(mock_discord_token):
    """Create DiscordMCPServer instance with mocked token"""
    with patch.dict(os.environ, {"DISCORD_TOKEN": mock_discord_token}):
        server = DiscordMCPServer()
        yield server
        # Cleanup
        if hasattr(server, 'client'):
            try:
                server.client.close()
            except:
                pass


@pytest.fixture
def mock_discord_api_responses():
    """Mock Discord API response data"""
    return {
        "message": {
            "id": "123456789012345678",
            "content": "Test message",
            "author": {
                "id": "987654321098765432",
                "username": "testuser"
            },
            "timestamp": "2023-01-01T12:00:00.000000+00:00"
        },
        "messages": [
            {
                "id": "123456789012345678",
                "content": "Test message 1",
                "author": {"username": "user1"},
                "timestamp": "2023-01-01T12:00:00.000000+00:00"
            },
            {
                "id": "123456789012345679",
                "content": "Test message 2", 
                "author": {"username": "user2"},
                "timestamp": "2023-01-01T12:01:00.000000+00:00"
            }
        ],
        "channels": [
            {
                "id": "123456789012345678",
                "name": "general",
                "type": 0
            },
            {
                "id": "123456789012345679",
                "name": "voice-channel",
                "type": 2
            }
        ],
        "guild": {
            "id": "123456789012345678",
            "name": "Test Server",
            "owner_id": "987654321098765432",
            "approximate_member_count": 100,
            "description": "A test Discord server"
        },
        "guilds": [
            {
                "id": "123456789012345678",
                "name": "Test Server 1"
            },
            {
                "id": "123456789012345679", 
                "name": "Test Server 2"
            }
        ],
        "thread": {
            "id": "123456789012345678",
            "name": "Test Thread",
            "type": 11
        },
        "channel_info": {
            "id": "123456789012345678",
            "name": "general",
            "type": 0,
            "guild_id": "guild_123456789012345678"
        },
        "active_threads": {
            "threads": [
                {
                    "id": "123456789012345678",
                    "name": "Active Thread 1",
                    "parent_id": "123456789012345678",
                    "member_count": 5,
                    "message_count": 20
                },
                {
                    "id": "123456789012345679",
                    "name": "Active Thread 2", 
                    "parent_id": "123456789012345678",
                    "member_count": 3,
                    "message_count": 15
                }
            ]
        },
        "archived_threads": {
            "threads": [
                {
                    "id": "123456789012345680",
                    "name": "Archived Thread 1",
                    "thread_metadata": {
                        "archive_timestamp": "2023-01-01T12:00:00.000000+00:00"
                    }
                }
            ]
        },
        "thread_members": [
            {
                "user_id": "987654321098765432",
                "join_timestamp": "2023-01-01T12:00:00.000000+00:00"
            },
            {
                "user_id": "987654321098765433",
                "join_timestamp": "2023-01-01T12:01:00.000000+00:00"
            }
        ]
    }
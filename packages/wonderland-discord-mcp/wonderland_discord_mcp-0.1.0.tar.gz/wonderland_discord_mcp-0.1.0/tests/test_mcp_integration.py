import pytest
import respx
import httpx
from mcp.types import TextContent
from main import DiscordMCPServer


class TestMCPToolIntegration:
    """Test MCP tool integration and end-to-end functionality"""

    async def test_mcp_server_initialization(self, discord_server):
        """Test MCP server initializes correctly"""
        assert discord_server.server is not None
        assert discord_server.client is not None
        assert discord_server.token == "test_token_123456789"

    async def test_all_discord_methods_exist(self, discord_server):
        """Test that Discord server has all expected methods"""
        expected_methods = [
            "send_message", "get_messages", "add_reaction",
            "list_channels", "get_channel_info", "create_thread",
            "get_server_info", "list_servers", "list_threads",
            "list_archived_threads", "join_thread", "get_thread_members"
        ]
        
        for method_name in expected_methods:
            assert hasattr(discord_server, method_name), f"Missing method: {method_name}"
            assert callable(getattr(discord_server, method_name)), f"Method not callable: {method_name}"

    @respx.mock
    async def test_send_message_functionality(self, discord_server, mock_discord_api_responses):
        """Test send_message functionality"""
        respx.post("https://discord.com/api/v10/channels/123456789012345678/messages").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["message"])
        )
        
        result = await discord_server.send_message(
            channel_id="123456789012345678", 
            content="Test message"
        )
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Message sent successfully" in result[0].text

    @respx.mock
    async def test_list_threads_functionality(self, discord_server, mock_discord_api_responses):
        """Test list_threads functionality"""
        # Mock channel info request first
        respx.get("https://discord.com/api/v10/channels/123456789012345678").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["channel_info"])
        )
        # Mock guild threads request
        respx.get("https://discord.com/api/v10/guilds/guild_123456789012345678/threads/active").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["active_threads"])
        )
        
        result = await discord_server.list_threads(channel_id="123456789012345678")
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Active Thread 1" in result[0].text

    async def test_discord_token_validation(self, discord_server):
        """Test Discord token is properly configured"""
        assert discord_server.token is not None
        assert discord_server.token == "test_token_123456789"

    async def test_http_client_configuration(self, discord_server):
        """Test HTTP client is properly configured"""
        assert discord_server.client is not None
        assert str(discord_server.client.base_url).rstrip('/') == "https://discord.com/api/v10"
        assert "Authorization" in discord_server.client.headers
        assert discord_server.client.headers["Authorization"] == "Bot test_token_123456789"

    async def test_error_handling_helper_method(self, discord_server):
        """Test the error handling helper method exists and works"""
        # Create a mock response with 404 error
        mock_response = httpx.Response(404, json={"message": "Not Found"})
        
        result = discord_server._handle_discord_error(mock_response, "messages")
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Not found" in result[0].text
        assert "Not Found" in result[0].text
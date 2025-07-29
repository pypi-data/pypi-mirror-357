import pytest
import respx
import httpx
from mcp.types import TextContent
from main import DiscordMCPServer


class TestDiscordMCPServer:
    """Test Discord MCP Server functionality"""

    @respx.mock
    async def test_send_message_success(self, discord_server, mock_discord_api_responses):
        """Test successful message sending"""
        # Mock Discord API response
        respx.post("https://discord.com/api/v10/channels/123456789012345678/messages").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["message"])
        )
        
        result = await discord_server.send_message("123456789012345678", "Hello, World!")
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Message sent successfully" in result[0].text
        assert "123456789012345678" in result[0].text

    @respx.mock
    async def test_send_message_with_reply(self, discord_server, mock_discord_api_responses):
        """Test sending message as reply"""
        respx.post("https://discord.com/api/v10/channels/123456789012345678/messages").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["message"])
        )
        
        result = await discord_server.send_message(
            "123456789012345678", 
            "Hello, World!", 
            reply_to="987654321098765432"
        )
        
        assert len(result) == 1
        assert "Message sent successfully" in result[0].text

    @respx.mock
    async def test_get_messages_success(self, discord_server, mock_discord_api_responses):
        """Test successful message retrieval"""
        respx.get("https://discord.com/api/v10/channels/123456789012345678/messages").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["messages"])
        )
        
        result = await discord_server.get_messages("123456789012345678", limit=10)
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "user1" in result[0].text
        assert "user2" in result[0].text
        assert "Test message 1" in result[0].text
        assert "Test message 2" in result[0].text

    @respx.mock
    async def test_add_reaction_success(self, discord_server):
        """Test successful reaction adding"""
        respx.put("https://discord.com/api/v10/channels/123456789012345678/messages/987654321098765432/reactions/👍/@me").mock(
            return_value=httpx.Response(204)
        )
        
        result = await discord_server.add_reaction("123456789012345678", "987654321098765432", "👍")
        
        assert len(result) == 1
        assert "Reaction 👍 added successfully" in result[0].text

    @respx.mock
    async def test_list_channels_success(self, discord_server, mock_discord_api_responses):
        """Test successful channel listing"""
        respx.get("https://discord.com/api/v10/guilds/123456789012345678/channels").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["channels"])
        )
        
        result = await discord_server.list_channels("123456789012345678")
        
        assert len(result) == 1
        assert "#general" in result[0].text
        assert "#voice-channel" in result[0].text
        assert "Type: 0" in result[0].text
        assert "Type: 2" in result[0].text

    @respx.mock
    async def test_list_channels_with_filter(self, discord_server, mock_discord_api_responses):
        """Test channel listing with type filter"""
        respx.get("https://discord.com/api/v10/guilds/123456789012345678/channels").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["channels"])
        )
        
        result = await discord_server.list_channels("123456789012345678", channel_type=0)
        
        assert len(result) == 1
        assert "#general" in result[0].text
        assert "#voice-channel" not in result[0].text

    @respx.mock
    async def test_get_server_info_success(self, discord_server, mock_discord_api_responses):
        """Test successful server info retrieval"""
        respx.get("https://discord.com/api/v10/guilds/123456789012345678").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["guild"])
        )
        
        result = await discord_server.get_server_info("123456789012345678")
        
        assert len(result) == 1
        assert "Test Server" in result[0].text
        assert "Member Count: 100" in result[0].text
        assert "A test Discord server" in result[0].text

    @respx.mock
    async def test_list_servers_success(self, discord_server, mock_discord_api_responses):
        """Test successful server listing"""
        respx.get("https://discord.com/api/v10/users/@me/guilds").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["guilds"])
        )
        
        result = await discord_server.list_servers()
        
        assert len(result) == 1
        assert "Test Server 1" in result[0].text
        assert "Test Server 2" in result[0].text

    @respx.mock
    async def test_create_thread_success(self, discord_server, mock_discord_api_responses):
        """Test successful thread creation"""
        respx.post("https://discord.com/api/v10/channels/123456789012345678/threads").mock(
            return_value=httpx.Response(201, json=mock_discord_api_responses["thread"])
        )
        
        result = await discord_server.create_thread("123456789012345678", "New Thread")
        
        assert len(result) == 1
        assert "Thread 'New Thread' created successfully" in result[0].text
        assert "123456789012345678" in result[0].text

    @respx.mock
    async def test_list_threads_success(self, discord_server, mock_discord_api_responses):
        """Test successful active thread listing"""
        # Mock channel info request first
        respx.get("https://discord.com/api/v10/channels/123456789012345678").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["channel_info"])
        )
        # Mock guild threads request
        respx.get("https://discord.com/api/v10/guilds/guild_123456789012345678/threads/active").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["active_threads"])
        )
        
        result = await discord_server.list_threads("123456789012345678")
        
        assert len(result) == 1
        assert "Active Thread 1" in result[0].text
        assert "Active Thread 2" in result[0].text
        assert "Members: 5" in result[0].text
        assert "Messages: 20" in result[0].text

    @respx.mock
    async def test_list_threads_empty(self, discord_server, mock_discord_api_responses):
        """Test thread listing with no threads"""
        # Mock channel info request first
        respx.get("https://discord.com/api/v10/channels/123456789012345678").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["channel_info"])
        )
        # Mock guild threads request with empty result
        respx.get("https://discord.com/api/v10/guilds/guild_123456789012345678/threads/active").mock(
            return_value=httpx.Response(200, json={"threads": []})
        )
        
        result = await discord_server.list_threads("123456789012345678")
        
        assert len(result) == 1
        assert "No active threads found" in result[0].text

    @respx.mock
    async def test_list_archived_threads_success(self, discord_server, mock_discord_api_responses):
        """Test successful archived thread listing"""
        respx.get("https://discord.com/api/v10/channels/123456789012345678/threads/archived/public").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["archived_threads"])
        )
        
        result = await discord_server.list_archived_threads("123456789012345678", type="public")
        
        assert len(result) == 1
        assert "Archived Thread 1" in result[0].text
        assert "2023-01-01T12:00:00" in result[0].text

    @respx.mock
    async def test_join_thread_success(self, discord_server):
        """Test successful thread joining"""
        respx.put("https://discord.com/api/v10/channels/123456789012345678/thread-members/@me").mock(
            return_value=httpx.Response(204)
        )
        
        result = await discord_server.join_thread("123456789012345678")
        
        assert len(result) == 1
        assert "Successfully joined thread 123456789012345678" in result[0].text

    @respx.mock
    async def test_get_thread_members_success(self, discord_server, mock_discord_api_responses):
        """Test successful thread members retrieval"""
        respx.get("https://discord.com/api/v10/channels/123456789012345678/thread-members").mock(
            return_value=httpx.Response(200, json=mock_discord_api_responses["thread_members"])
        )
        
        result = await discord_server.get_thread_members("123456789012345678")
        
        assert len(result) == 1
        assert "987654321098765432" in result[0].text
        assert "987654321098765433" in result[0].text
        assert "2023-01-01T12:00:00" in result[0].text

    @respx.mock
    async def test_get_thread_members_empty(self, discord_server):
        """Test thread members retrieval with no members"""
        respx.get("https://discord.com/api/v10/channels/123456789012345678/thread-members").mock(
            return_value=httpx.Response(200, json=[])
        )
        
        result = await discord_server.get_thread_members("123456789012345678")
        
        assert len(result) == 1
        assert "No members found in this thread" in result[0].text
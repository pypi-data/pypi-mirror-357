import pytest
import respx
import httpx
from mcp.types import TextContent
from main import DiscordMCPServer


class TestErrorHandling:
    """Test error handling for various Discord API failures"""

    async def _call_tool(self, discord_server, tool_name: str, arguments: dict):
        """Helper to call Discord server methods directly"""
        if tool_name == "send_message":
            return await discord_server.send_message(**arguments)
        elif tool_name == "get_messages":
            return await discord_server.get_messages(**arguments)
        elif tool_name == "add_reaction":
            return await discord_server.add_reaction(**arguments)
        elif tool_name == "list_channels":
            return await discord_server.list_channels(**arguments)
        elif tool_name == "create_thread":
            return await discord_server.create_thread(**arguments)
        elif tool_name == "list_threads":
            return await discord_server.list_threads(**arguments)
        elif tool_name == "join_thread":
            return await discord_server.join_thread(**arguments)
        elif tool_name == "get_thread_members":
            return await discord_server.get_thread_members(**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    @respx.mock
    async def test_send_message_404_error(self, discord_server):
        """Test handling 404 error when sending message to invalid channel"""
        respx.post("https://discord.com/api/v10/channels/invalid_channel/messages").mock(
            return_value=httpx.Response(404, json={"message": "Unknown Channel"})
        )
        
        result = await self._call_tool(discord_server, "send_message", {
            "channel_id": "invalid_channel", 
            "content": "Test message"
        })
        
        assert len(result) == 1
        assert any(keyword in result[0].text for keyword in ["Permission denied:", "Not found:", "Rate limited:", "Discord API error", "Bad request:"])

    @respx.mock
    async def test_send_message_403_error(self, discord_server):
        """Test handling 403 permission error"""
        respx.post("https://discord.com/api/v10/channels/123456789012345678/messages").mock(
            return_value=httpx.Response(403, json={"message": "Missing Permissions"})
        )
        
        result = await self._call_tool(discord_server, "send_message", {
            "channel_id": "123456789012345678", 
            "content": "Test message"
        })
        
        assert len(result) == 1
        assert any(keyword in result[0].text for keyword in ["Permission denied:", "Not found:", "Rate limited:", "Discord API error", "Bad request:"])

    @respx.mock
    async def test_send_message_rate_limit_error(self, discord_server):
        """Test handling 429 rate limit error"""
        respx.post("https://discord.com/api/v10/channels/123456789012345678/messages").mock(
            return_value=httpx.Response(429, json={
                "message": "You are being rate limited.",
                "retry_after": 5.0
            })
        )
        
        result = await self._call_tool(discord_server, "send_message", {
            "channel_id": "123456789012345678", 
            "content": "Test message"
        })
        
        assert len(result) == 1
        assert any(keyword in result[0].text for keyword in ["Permission denied:", "Not found:", "Rate limited:", "Discord API error", "Bad request:"])

    @respx.mock
    async def test_get_messages_unauthorized_error(self, discord_server):
        """Test handling 401 unauthorized error"""
        respx.get("https://discord.com/api/v10/channels/123456789012345678/messages").mock(
            return_value=httpx.Response(401, json={"message": "401: Unauthorized"})
        )
        
        result = await self._call_tool(discord_server, "get_messages", {
            "channel_id": "123456789012345678"
        })
        
        assert len(result) == 1
        assert any(keyword in result[0].text for keyword in ["Permission denied:", "Not found:", "Rate limited:", "Discord API error", "Bad request:"])

    @respx.mock
    async def test_list_channels_server_error(self, discord_server):
        """Test handling 500 server error"""
        respx.get("https://discord.com/api/v10/guilds/123456789012345678/channels").mock(
            return_value=httpx.Response(500, json={"message": "Internal Server Error"})
        )
        
        result = await self._call_tool(discord_server, "list_channels", {
            "server_id": "123456789012345678"
        })
        
        assert len(result) == 1
        assert any(keyword in result[0].text for keyword in ["Permission denied:", "Not found:", "Rate limited:", "Discord API error", "Bad request:"])

    @respx.mock
    async def test_add_reaction_invalid_emoji_error(self, discord_server):
        """Test handling invalid emoji error"""
        respx.put("https://discord.com/api/v10/channels/123456789012345678/messages/987654321098765432/reactions/invalid_emoji/@me").mock(
            return_value=httpx.Response(400, json={"message": "Invalid Form Body"})
        )
        
        result = await self._call_tool(discord_server, "add_reaction", {
            "channel_id": "123456789012345678", 
            "message_id": "987654321098765432", 
            "emoji": "invalid_emoji"
        })
        
        assert len(result) == 1
        assert any(keyword in result[0].text for keyword in ["Permission denied:", "Not found:", "Rate limited:", "Discord API error", "Bad request:"])

    @respx.mock
    async def test_create_thread_no_permission_error(self, discord_server):
        """Test handling permission error when creating thread"""
        respx.post("https://discord.com/api/v10/channels/123456789012345678/threads").mock(
            return_value=httpx.Response(403, json={"message": "Missing Permissions"})
        )
        
        result = await self._call_tool(discord_server, "create_thread", {
            "channel_id": "123456789012345678", 
            "name": "Test Thread"
        })
        
        assert len(result) == 1
        assert any(keyword in result[0].text for keyword in ["Permission denied:", "Not found:", "Rate limited:", "Discord API error", "Bad request:"])

    @respx.mock
    async def test_list_threads_channel_not_found(self, discord_server):
        """Test handling channel not found error when listing threads"""
        # Mock the channel info request that fails
        respx.get("https://discord.com/api/v10/channels/invalid_channel").mock(
            return_value=httpx.Response(404, json={"message": "Unknown Channel"})
        )
        
        result = await self._call_tool(discord_server, "list_threads", {
            "channel_id": "invalid_channel"
        })
        
        assert len(result) == 1
        assert any(keyword in result[0].text for keyword in ["Permission denied:", "Not found:", "Rate limited:", "Discord API error", "Bad request:"])

    @respx.mock
    async def test_join_thread_already_member_error(self, discord_server):
        """Test handling error when already a member of thread"""
        respx.put("https://discord.com/api/v10/channels/123456789012345678/thread-members/@me").mock(
            return_value=httpx.Response(400, json={"message": "Target user is already a member"})
        )
        
        result = await self._call_tool(discord_server, "join_thread", {
            "thread_id": "123456789012345678"
        })
        
        assert len(result) == 1
        assert any(keyword in result[0].text for keyword in ["Permission denied:", "Not found:", "Rate limited:", "Discord API error", "Bad request:"])

    @respx.mock
    async def test_get_thread_members_thread_not_found(self, discord_server):
        """Test handling thread not found error"""
        respx.get("https://discord.com/api/v10/channels/invalid_thread/thread-members").mock(
            return_value=httpx.Response(404, json={"message": "Unknown Channel"})
        )
        
        result = await self._call_tool(discord_server, "get_thread_members", {
            "thread_id": "invalid_thread"
        })
        
        assert len(result) == 1
        assert any(keyword in result[0].text for keyword in ["Permission denied:", "Not found:", "Rate limited:", "Discord API error", "Bad request:"])

    @respx.mock
    async def test_network_timeout_error(self, discord_server):
        """Test handling network timeout errors"""
        respx.get("https://discord.com/api/v10/channels/123456789012345678/messages").mock(
            side_effect=httpx.TimeoutException("Request timed out")
        )
        
        result = await self._call_tool(discord_server, "get_messages", {
            "channel_id": "123456789012345678"
        })
        
        assert len(result) == 1
        assert "Network error:" in result[0].text

    @respx.mock
    async def test_connection_error(self, discord_server):
        """Test handling connection errors"""
        respx.get("https://discord.com/api/v10/channels/123456789012345678/messages").mock(
            side_effect=httpx.ConnectError("Connection failed")
        )
        
        result = await self._call_tool(discord_server, "get_messages", {
            "channel_id": "123456789012345678"
        })
        
        assert len(result) == 1
        assert "Network error:" in result[0].text

    async def test_invalid_parameters(self, discord_server):
        """Test handling of invalid parameters passed to methods"""
        result = await self._call_tool(discord_server, "send_message", {
            "channel_id": "", 
            "content": "Test message"
        })
        
        # The method should handle empty strings gracefully
        assert len(result) == 1
        assert any(keyword in result[0].text for keyword in ["Permission denied:", "Not found:", "Rate limited:", "Discord API error", "Bad request:"])
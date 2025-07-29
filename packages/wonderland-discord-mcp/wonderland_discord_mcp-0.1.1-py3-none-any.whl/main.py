#!/usr/bin/env python3

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DISCORD_API_BASE = "https://discord.com/api/v10"


class DiscordMCPServer:
    def __init__(self):
        self.token = os.getenv("DISCORD_TOKEN")
        if not self.token:
            raise ValueError("DISCORD_TOKEN environment variable is required")

        self.client = httpx.AsyncClient(
            base_url=DISCORD_API_BASE,
            headers={
                "Authorization": f"Bot {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "DiscordMCPServer/1.0",
            },
        )

        self.server = Server("discord-mcp-server")
        self._register_tools()

    def _handle_discord_error(self, response: httpx.Response, context: str = "") -> List[TextContent]:
        """Handle Discord API error responses with specific error messages"""
        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
        error_message = error_data.get('message', 'Unknown error')
        
        if response.status_code == 403:
            permission_hints = {
                "messages": "Bot may lack 'Send Messages' permission",
                "reactions": "Bot may lack 'Add Reactions' permission", 
                "threads": "Bot may lack 'Create Public Threads' permission",
                "channels": "Bot may lack 'View Channels' permission"
            }
            hint = permission_hints.get(context, "Bot may lack required permissions")
            return [TextContent(type="text", text=f"Permission denied: {error_message}. {hint} in this channel/server.")]
        elif response.status_code == 404:
            return [TextContent(type="text", text=f"Not found: {error_message}. Check if the ID is correct and bot has access.")]
        elif response.status_code == 429:
            return [TextContent(type="text", text=f"Rate limited: {error_message}. Please wait before making another request.")]
        elif response.status_code == 400:
            return [TextContent(type="text", text=f"Bad request: {error_message}. Check your input parameters.")]
        else:
            return [TextContent(type="text", text=f"Discord API error ({response.status_code}): {error_message}")]

    def _register_tools(self):
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="send_message",
                    description="Send a message to a Discord channel with support for mentions, formatting, and replies",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "Discord channel ID",
                            },
                            "content": {
                                "type": "string",
                                "description": "Message content. Supports Discord markdown formatting (**bold**, *italic*, `code`) and mentions. For mentions use: <@USER_ID> for users (NOT <@!USER_ID>), <@&ROLE_ID> for roles, <#CHANNEL_ID> for channels, @everyone for everyone, @here for online users. Example: '<@123456789> Your task is ready!'",
                            },
                            "reply_to": {
                                "type": "string",
                                "description": "Message ID to reply to (optional)",
                            },
                        },
                        "required": ["channel_id", "content"],
                    },
                ),
                Tool(
                    name="get_messages",
                    description="Get messages from a Discord channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "Discord channel ID",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of messages to retrieve (max 100)",
                                "default": 50,
                            },
                            "before": {
                                "type": "string",
                                "description": "Get messages before this message ID",
                            },
                            "after": {
                                "type": "string",
                                "description": "Get messages after this message ID",
                            },
                        },
                        "required": ["channel_id"],
                    },
                ),
                Tool(
                    name="add_reaction",
                    description="Add a reaction to a Discord message",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "Discord channel ID",
                            },
                            "message_id": {
                                "type": "string",
                                "description": "Discord message ID",
                            },
                            "emoji": {
                                "type": "string",
                                "description": "Emoji to react with (unicode or custom format)",
                            },
                        },
                        "required": ["channel_id", "message_id", "emoji"],
                    },
                ),
                Tool(
                    name="list_channels",
                    description="List channels in a Discord server",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_id": {
                                "type": "string",
                                "description": "Discord server (guild) ID",
                            },
                            "channel_type": {
                                "type": "integer",
                                "description": "Filter by channel type (0=text, 2=voice, etc.)",
                            },
                        },
                        "required": ["server_id"],
                    },
                ),
                Tool(
                    name="get_channel_info",
                    description="Get information about a Discord channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "Discord channel ID",
                            }
                        },
                        "required": ["channel_id"],
                    },
                ),
                Tool(
                    name="create_thread",
                    description="Create a new thread in a Discord channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "Discord channel ID",
                            },
                            "name": {"type": "string", "description": "Thread name"},
                            "message_id": {
                                "type": "string",
                                "description": "Message ID to create thread from (optional)",
                            },
                        },
                        "required": ["channel_id", "name"],
                    },
                ),
                Tool(
                    name="get_server_info",
                    description="Get information about a Discord server",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "server_id": {
                                "type": "string",
                                "description": "Discord server (guild) ID",
                            }
                        },
                        "required": ["server_id"],
                    },
                ),
                Tool(
                    name="list_servers",
                    description="List Discord servers the bot has access to",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="list_threads",
                    description="List active threads in a Discord channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "Discord channel ID",
                            }
                        },
                        "required": ["channel_id"],
                    },
                ),
                Tool(
                    name="list_archived_threads",
                    description="List archived threads in a Discord channel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "channel_id": {
                                "type": "string",
                                "description": "Discord channel ID",
                            },
                            "type": {
                                "type": "string",
                                "enum": ["public", "private"],
                                "description": "Type of archived threads to list",
                                "default": "public",
                            },
                            "before": {
                                "type": "string",
                                "description": "Get threads before this timestamp",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of threads to retrieve (max 100)",
                                "default": 50,
                            },
                        },
                        "required": ["channel_id"],
                    },
                ),
                Tool(
                    name="join_thread",
                    description="Join a Discord thread",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {
                                "type": "string",
                                "description": "Discord thread ID",
                            }
                        },
                        "required": ["thread_id"],
                    },
                ),
                Tool(
                    name="get_thread_members",
                    description="Get members of a Discord thread",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {
                                "type": "string",
                                "description": "Discord thread ID",
                            }
                        },
                        "required": ["thread_id"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "send_message":
                    return await self.send_message(**arguments)
                elif name == "get_messages":
                    return await self.get_messages(**arguments)
                elif name == "add_reaction":
                    return await self.add_reaction(**arguments)
                elif name == "list_channels":
                    return await self.list_channels(**arguments)
                elif name == "get_channel_info":
                    return await self.get_channel_info(**arguments)
                elif name == "create_thread":
                    return await self.create_thread(**arguments)
                elif name == "get_server_info":
                    return await self.get_server_info(**arguments)
                elif name == "list_servers":
                    return await self.list_servers(**arguments)
                elif name == "list_threads":
                    return await self.list_threads(**arguments)
                elif name == "list_archived_threads":
                    return await self.list_archived_threads(**arguments)
                elif name == "join_thread":
                    return await self.join_thread(**arguments)
                elif name == "get_thread_members":
                    return await self.get_thread_members(**arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def send_message(
        self, channel_id: str, content: str, reply_to: Optional[str] = None
    ) -> List[TextContent]:
        payload = {"content": content}
        if reply_to:
            payload["message_reference"] = {"message_id": reply_to}

        response = await self.client.post(
            f"/channels/{channel_id}/messages", json=payload
        )
        
        if response.status_code != 200:
            return self._handle_discord_error(response, "messages")

        message_data = response.json()
        return [
            TextContent(
                type="text", text=f"Message sent successfully. ID: {message_data['id']}"
            )
        ]

    async def get_messages(
        self,
        channel_id: str,
        limit: int = 50,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> List[TextContent]:
        params = {"limit": min(limit, 100)}
        if before:
            params["before"] = before
        if after:
            params["after"] = after

        try:
            response = await self.client.get(
                f"/channels/{channel_id}/messages", params=params
            )
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            return [TextContent(type="text", text=f"Network error: {str(e)}")]
        
        if response.status_code != 200:
            return self._handle_discord_error(response, "messages")

        messages = response.json()

        formatted_messages = []
        for msg in messages:
            author = msg.get("author", {})
            timestamp = msg.get("timestamp", "")
            content = msg.get("content", "")
            formatted_messages.append(
                f"[{timestamp}] {author.get('username', 'Unknown')}: {content}"
            )

        return [TextContent(type="text", text="\n".join(formatted_messages))]

    async def add_reaction(
        self, channel_id: str, message_id: str, emoji: str
    ) -> List[TextContent]:
        # URL encode emoji to handle special characters and Unicode properly
        encoded_emoji = quote(emoji, safe="")
        response = await self.client.put(
            f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me"
        )
        
        if response.status_code != 204:  # Discord returns 204 for successful reactions
            return self._handle_discord_error(response, "reactions")

        return [TextContent(type="text", text=f"Reaction {emoji} added successfully")]

    async def list_channels(
        self, server_id: str, channel_type: Optional[int] = None
    ) -> List[TextContent]:
        response = await self.client.get(f"/guilds/{server_id}/channels")
        
        if response.status_code != 200:
            return self._handle_discord_error(response, "channels")

        channels = response.json()
        if channel_type is not None:
            channels = [ch for ch in channels if ch.get("type") == channel_type]

        formatted_channels = []
        for channel in channels:
            name = channel.get("name", "Unknown")
            ch_id = channel.get("id", "")
            ch_type = channel.get("type", 0)
            formatted_channels.append(f"#{name} (ID: {ch_id}, Type: {ch_type})")

        return [TextContent(type="text", text="\n".join(formatted_channels))]

    async def get_channel_info(self, channel_id: str) -> List[TextContent]:
        response = await self.client.get(f"/channels/{channel_id}")
        if response.status_code != 200:
            return self._handle_discord_error(response, "channels")

        channel = response.json()

        info = f"Channel: #{channel.get('name', 'Unknown')}\n"
        info += f"ID: {channel.get('id')}\n"
        info += f"Type: {channel.get('type')}\n"
        info += f"Topic: {channel.get('topic', 'None')}\n"
        info += f"Guild ID: {channel.get('guild_id', 'N/A')}"

        return [TextContent(type="text", text=info)]

    async def create_thread(
        self, channel_id: str, name: str, message_id: Optional[str] = None
    ) -> List[TextContent]:
        if message_id:
            # Create thread from message
            response = await self.client.post(
                f"/channels/{channel_id}/messages/{message_id}/threads",
                json={
                    "name": name,
                    "auto_archive_duration": 1440,  # 24 hours (required parameter)
                },
            )
        else:
            # Create public thread without message
            response = await self.client.post(
                f"/channels/{channel_id}/threads",
                json={
                    "name": name,
                    "type": 11,  # PUBLIC_THREAD
                    "auto_archive_duration": 1440,  # 24 hours (required parameter)
                },
            )

        if response.status_code != 201:  # Discord returns 201 for created threads
            return self._handle_discord_error(response, "threads")

        thread_data = response.json()
        return [
            TextContent(
                type="text",
                text=f"Thread '{name}' created successfully. ID: {thread_data['id']}",
            )
        ]

    async def get_server_info(self, server_id: str) -> List[TextContent]:
        response = await self.client.get(f"/guilds/{server_id}")
        if response.status_code != 200:
            return self._handle_discord_error(response, "channels")

        guild = response.json()

        info = f"Server: {guild.get('name', 'Unknown')}\n"
        info += f"ID: {guild.get('id')}\n"
        info += f"Owner ID: {guild.get('owner_id')}\n"
        info += f"Member Count: {guild.get('approximate_member_count', 'Unknown')}\n"
        info += f"Description: {guild.get('description', 'None')}"

        return [TextContent(type="text", text=info)]

    async def list_servers(self) -> List[TextContent]:
        response = await self.client.get("/users/@me/guilds")
        if response.status_code != 200:
            return self._handle_discord_error(response, "channels")

        guilds = response.json()

        formatted_guilds = []
        for guild in guilds:
            name = guild.get("name", "Unknown")
            guild_id = guild.get("id", "")
            formatted_guilds.append(f"{name} (ID: {guild_id})")

        return [TextContent(type="text", text="\n".join(formatted_guilds))]

    async def list_threads(self, channel_id: str) -> List[TextContent]:
        # First get the guild_id from the channel
        channel_response = await self.client.get(f"/channels/{channel_id}")
        if channel_response.status_code != 200:
            return self._handle_discord_error(channel_response, "channels")
        
        channel_data = channel_response.json()
        guild_id = channel_data.get("guild_id")
        if not guild_id:
            return [TextContent(type="text", text="Could not determine guild ID for this channel.")]

        # Use the correct endpoint for active threads
        response = await self.client.get(f"/guilds/{guild_id}/threads/active")
        if response.status_code != 200:
            return self._handle_discord_error(response, "threads")

        data = response.json()
        threads = data.get("threads", [])
        has_more = data.get("has_more", False)

        # Filter threads to only show those in the requested channel
        channel_threads = [t for t in threads if t.get("parent_id") == channel_id]

        formatted_threads = []
        for thread in channel_threads:
            name = thread.get("name", "Unknown")
            thread_id = thread.get("id", "")
            member_count = thread.get("member_count", 0)
            message_count = thread.get("message_count", 0)
            formatted_threads.append(
                f"#{name} (ID: {thread_id}, Members: {member_count}, Messages: {message_count})"
            )

        if not formatted_threads:
            return [
                TextContent(
                    type="text", text="No active threads found in this channel."
                )
            ]

        result_text = "\n".join(formatted_threads)
        if has_more:
            result_text += (
                f"\n\n(Note: More threads available - showing {len(threads)} results)"
            )

        return [TextContent(type="text", text=result_text)]

    async def list_archived_threads(
        self,
        channel_id: str,
        type: str = "public",
        before: Optional[str] = None,
        limit: int = 50,
    ) -> List[TextContent]:
        endpoint = (
            f"/channels/{channel_id}/threads/archived/public"
            if type == "public"
            else f"/channels/{channel_id}/threads/archived/private"
        )

        params = {"limit": min(limit, 100)}
        if before:
            params["before"] = before

        response = await self.client.get(endpoint, params=params)
        if response.status_code != 200:
            return self._handle_discord_error(response, "threads")

        data = response.json()
        threads = data.get("threads", [])
        has_more = data.get("has_more", False)

        formatted_threads = []
        for thread in threads:
            name = thread.get("name", "Unknown")
            thread_id = thread.get("id", "")
            archive_timestamp = thread.get("thread_metadata", {}).get(
                "archive_timestamp", ""
            )
            formatted_threads.append(
                f"#{name} (ID: {thread_id}, Archived: {archive_timestamp})"
            )

        if not formatted_threads:
            return [
                TextContent(
                    type="text",
                    text=f"No {type} archived threads found in this channel.",
                )
            ]

        result_text = "\n".join(formatted_threads)
        if has_more:
            result_text += (
                f"\n\n(Note: More threads available - showing {len(threads)} results)"
            )

        return [TextContent(type="text", text=result_text)]

    async def join_thread(self, thread_id: str) -> List[TextContent]:
        response = await self.client.put(f"/channels/{thread_id}/thread-members/@me")
        if response.status_code != 204:  # Discord returns 204 for successful join
            return self._handle_discord_error(response, "threads")

        return [
            TextContent(type="text", text=f"Successfully joined thread {thread_id}")
        ]

    async def get_thread_members(self, thread_id: str) -> List[TextContent]:
        response = await self.client.get(f"/channels/{thread_id}/thread-members")
        if response.status_code != 200:
            return self._handle_discord_error(response, "threads")

        members = response.json()

        formatted_members = []
        for member in members:
            user_info = member.get("user_id", "Unknown")
            join_timestamp = member.get("join_timestamp", "")
            formatted_members.append(f"User ID: {user_info} (Joined: {join_timestamp})")

        if not formatted_members:
            return [TextContent(type="text", text="No members found in this thread.")]

        return [TextContent(type="text", text="\n".join(formatted_members))]

    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream, self.server.create_initialization_options()
            )


async def main():
    server = DiscordMCPServer()
    await server.run()


def cli_main():
    """Entry point for the CLI command"""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()

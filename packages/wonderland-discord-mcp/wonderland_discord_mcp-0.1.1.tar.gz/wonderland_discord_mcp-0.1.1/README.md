# Discord MCP Server

Discord MCP Server provides Discord API integration for MCP-compatible AI models through a simple, secure server.

## 🚀 Quick Start with uvx (Recommended)

The easiest way to use Discord MCP Server is with `uvx` - no installation required:

```bash
# Set your Discord bot token
export DISCORD_TOKEN="your_bot_token_here"

# Run directly with uvx (no installation needed!)
uvx discord-mcp
```

## 🛠 Alternative Installation Methods

### Using pipx
```bash
pipx install discord-mcp
export DISCORD_TOKEN="your_bot_token_here"
discord-mcp
```

### Using pip
```bash
pip install discord-mcp
export DISCORD_TOKEN="your_bot_token_here" 
discord-mcp
```

### Development Installation
```bash
git clone https://github.com/defi-wonderland/discord-mcp
cd discord-mcp
uv add mcp httpx python-dotenv
cp .env.example .env  # Add your Discord token
uv run python -m discord_mcp
```

## 🔧 Discord Bot Setup

1. Go to https://discord.com/developers/applications
2. Create a new application and bot
3. Copy the bot token to your environment or `.env` file
4. Invite the bot to your server with these permissions:
   - View Channels
   - Send Messages
   - Read Message History  
   - Add Reactions
   - Create Public Threads

## 🔨 Available Tools (12 Total)

### Message Operations
- **send_message** - Send messages with mentions, formatting, and replies
- **get_messages** - Retrieve message history with pagination
- **add_reaction** - Add emoji reactions to messages

### Channel Management  
- **list_channels** - List server channels with type filtering
- **get_channel_info** - Get detailed channel information

### Thread Discovery & Management
- **create_thread** - Create new discussion threads
- **list_threads** - Discover active threads in channels
- **list_archived_threads** - Find archived threads (public/private)
- **join_thread** - Join existing threads
- **get_thread_members** - View thread membership

### Server Information
- **get_server_info** - Get server details and member counts
- **list_servers** - List all accessible Discord servers

## ✨ Features

- **Zero Installation**: Run directly with `uvx discord-mcp`
- **Direct REST API**: No persistent bot process required
- **Comprehensive Error Handling**: Helpful error messages with permission hints
- **Discord Formatting**: Full support for markdown and mentions
- **Thread Management**: Complete thread discovery and interaction
- **Secure**: Minimal permissions, read-only server access
- **MCP Standard**: Compatible with Claude Desktop and other MCP clients

## 🔗 Integration with MCP Clients

### Claude Desktop
Add to your Claude Desktop MCP configuration:
```json
{
  "mcpServers": {
    "discord": {
      "command": "uvx",
      "args": ["discord-mcp"],
      "env": {
        "DISCORD_TOKEN": "your_bot_token_here"
      }
    }
  }
}
```

### Other MCP Clients
The server communicates via stdio and follows the MCP protocol standard.

## 📝 Usage Examples

### Send a Message with Mentions
```json
{
  "tool": "send_message",
  "arguments": {
    "channel_id": "123456789",
    "content": "Hello <@987654321>! Check out <#555666777>"
  }
}
```

### Create and Manage Threads
```json
{
  "tool": "create_thread", 
  "arguments": {
    "channel_id": "123456789",
    "name": "Discussion Thread"
  }
}
```

## 🤝 Contributing

This project is open source and contributions are welcome! See the repository for development setup and contribution guidelines.

## 📄 License

MIT License - see LICENSE file for details.
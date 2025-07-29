# Discord MCP Server

## Project Purpose

This project creates a simple, agnostic Model Context Protocol (MCP) server that exposes Discord API functionality to AI models. The MCP server makes direct REST API calls to Discord without running a persistent bot process, providing a standardized interface that allows any MCP-compatible AI to interact with Discord servers through well-defined tools.

## Objective

Create a minimal, secure Discord MCP server that:
- Exposes core Discord operations as standardized MCP tools
- Maintains minimal permissions for security
- Provides a foundation for future AI-powered Discord integrations
- Remains agnostic to specific AI models or use cases

## Final Architecture & Tech Stack

### Core Framework
- **Language**: Python 3.10+ (required by MCP SDK)
- **MCP Framework**: Official Python MCP SDK (`mcp` package v1.9.4+)
- **HTTP Client**: `httpx` for Discord REST API calls
- **Package Manager**: UV (recommended by MCP community)

### Discord Integration
- **API**: Discord REST API v10 (direct HTTP calls)
- **Authentication**: Bearer token via Discord Application
- **Architecture**: Stateless MCP server (no persistent bot process)
- **Approach**: Direct REST calls (not Discord.py SDK)

### Development Dependencies
- **Testing**: pytest with pytest-asyncio for async support
- **HTTP Mocking**: respx for Discord API response mocking
- **Code Quality**: black (formatting), ruff (linting)
- **Environment**: python-dotenv for configuration

### Installation Commands
```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone/setup project
cd discord-mcp
uv python pin 3.10  # Ensure Python 3.10+
uv add mcp httpx python-dotenv
uv add --dev pytest pytest-asyncio respx black ruff

# Run the server
cp .env.example .env  # Add your Discord token
uv run python main.py
```

## Development Plan

### Phase 1: Foundation Setup ✅ COMPLETED
- [x] Initialize project structure
- [x] Set up Discord application and API token support
- [x] Implement basic MCP server scaffolding
- [x] Configure minimal Discord permissions

### Phase 2: Core Message Operations ✅ COMPLETED
- [x] `send_message(channel_id, content, reply_to=None)`
- [x] `get_messages(channel_id, limit=50, before=None, after=None)`
- [x] `add_reaction(channel_id, message_id, emoji)`

### Phase 3: Channel & Thread Management ✅ COMPLETED
- [x] `list_channels(server_id, channel_type=None)`
- [x] `get_channel_info(channel_id)`
- [x] `create_thread(channel_id, name, message_id=None)`
- [x] `list_threads(channel_id)` - Active threads discovery
- [x] `list_archived_threads(channel_id, type="public|private")` - Archived threads
- [x] `join_thread(thread_id)`
- [x] `get_thread_members(thread_id)` - Thread membership info

### Phase 4: Server Information ✅ COMPLETED
- [x] `get_server_info(server_id)`
- [x] `list_servers()`
- [ ] `get_server_members(server_id, limit=100)` - Not implemented (requires additional permissions)
- [ ] `get_member_info(server_id, user_id)` - Not implemented (requires additional permissions)

### Phase 5: User Operations 🚧 FUTURE
- [ ] `get_user_info(user_id)` - Future enhancement
- [ ] `send_dm(user_id, content)` - Future enhancement

### Phase 6: Search & Discovery 🚧 FUTURE  
- [ ] `search_messages(query, channel_id=None, author_id=None, limit=25)` - Future enhancement
- [ ] `find_channels_by_name(server_id, name_pattern)` - Future enhancement

### Phase 7: Testing & Documentation ✅ COMPLETED
- [x] Unit tests for all implemented MCP tools (15 core tests)
- [x] Integration tests with mocked Discord API responses
- [x] Error handling tests for various failure scenarios
- [x] Test fixtures and comprehensive test coverage
- [x] API documentation in code and README

## Required Discord Application Permissions

- View Channels
- Send Messages
- Read Message History
- Add Reactions
- Create Public Threads
- View Server Members (optional)

## Implemented MCP Tools (12 Total)

### Message Operations (3 tools)
- `send_message` - Send messages with optional replies
- `get_messages` - Retrieve message history with pagination  
- `add_reaction` - Add emoji reactions to messages

### Channel Management (2 tools)
- `list_channels` - List all channels in a server with type filtering
- `get_channel_info` - Get detailed channel information

### Thread Discovery & Management (5 tools)
- `create_thread` - Create new threads (public/from message)
- `list_threads` - Discover active threads in channels
- `list_archived_threads` - Find archived threads (public/private)
- `join_thread` - Join existing threads
- `get_thread_members` - View thread membership

### Server Information (2 tools)
- `get_server_info` - Get server details and member counts
- `list_servers` - List all accessible Discord servers

## Testing Infrastructure

### Test Coverage
- **15 Core Function Tests**: All implemented Discord API methods
- **13 Error Handling Tests**: HTTP errors, timeouts, malformed responses  
- **9 Integration Tests**: MCP tool registration and schema validation
- **Test Framework**: pytest with async support and HTTP mocking via respx

### Running Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test categories
uv run pytest tests/test_discord_mcp.py -v          # Core functionality
uv run pytest tests/test_error_handling.py -v      # Error scenarios  
uv run pytest tests/test_mcp_integration.py -v     # MCP integration
```

## Security Considerations

- No message editing or deletion capabilities
- No administrative permissions
- Read-only access to server information
- Minimal permission set to reduce attack surface
- No access to sensitive user data beyond public information

## Future Extensions

This MCP server provides a foundation for building more sophisticated Discord integrations:
- AI-powered meeting notes
- Task management integration
- Code analysis tools
- Smart scheduling features

## Design Decisions Log

*This section tracks all architectural and design decisions made during development.*

### 2025-06-21: Initial Architecture Decisions
- **MCP vs Bot**: Chose MCP server over traditional Discord bot for AI model compatibility
- **REST vs SDK**: Direct REST API calls instead of Discord.py to keep dependencies minimal
- **Python vs TypeScript**: Python chosen due to mature official MCP SDK support
- **No Persistent Process**: Stateless server that makes API calls on-demand only
- **Minimal Permissions**: Read/write only, no edit/delete to maintain security
- **Tools Selected**: 12 core Discord operations covering messages, channels, threads, server info

### 2025-06-21: Thread Discovery Implementation
- **Thread Limitation Discovered**: Discord threads are not visible through channel listing APIs
- **Solution**: Added dedicated thread discovery tools (`list_threads`, `list_archived_threads`)
- **Comprehensive Coverage**: Active threads, archived public/private threads, thread membership
- **User Request**: Implementation prioritized based on heavy thread usage in Discord communities

### 2025-06-21: Testing Strategy
- **Framework Choice**: pytest-asyncio chosen for async Discord API testing
- **Mocking Strategy**: respx library for HTTP request/response mocking
- **Test Categories**: Core functionality, error handling, MCP integration testing
- **Coverage**: 37 total tests covering all implemented functionality and error scenarios

### Future Decision Template
*Use this format for tracking new decisions:*
- **Date**: YYYY-MM-DD
- **Decision**: Brief description
- **Rationale**: Why this approach was chosen
- **Alternatives Considered**: What other options were evaluated
- **Impact**: How this affects the project

## Getting Started

### Quick Start
1. **Setup Dependencies**: Install UV and project dependencies (see Installation Commands above)
2. **Discord Application**: Create Discord application at https://discord.com/developers/applications
3. **Bot Token**: Generate bot token and add to `.env` file (copy from `.env.example`)
4. **Permissions**: Configure bot permissions (View Channels, Send Messages, Read Message History, Add Reactions, Create Public Threads)
5. **Run Server**: `uv run python main.py` to start the MCP server
6. **Test Integration**: Connect MCP-compatible AI client (Claude Desktop, etc.) to test tools

### Project Status: ✅ PRODUCTION READY
- **Core Implementation**: Complete with 12 Discord tools
- **Thread Discovery**: Full support for active and archived thread discovery  
- **Error Handling**: Comprehensive error handling for all Discord API scenarios
- **Testing**: 37 tests with 100% coverage of implemented functionality
- **Documentation**: Complete API documentation and usage examples

## Discord Mention Guidelines

### Proper Mention Syntax
When using the `send_message` tool, follow these mention formats for proper functionality:

**✅ CORRECT Mention Formats:**
- **Users**: `<@USER_ID>` (e.g., `<@123456789012345678>`)
- **Roles**: `<@&ROLE_ID>` (e.g., `<@&987654321098765432>`)
- **Channels**: `<#CHANNEL_ID>` (e.g., `<#111222333444555666>`)
- **Everyone**: `@everyone` (requires "Mention Everyone" permission)
- **Here**: `@here` (mentions only online users)

**❌ INCORRECT Formats:**
- `<@!USER_ID>` (with exclamation - gets silently dropped by Discord)
- `@username` (plain text, won't create actual mention)

**Getting User/Role/Channel IDs:**
1. Enable Developer Mode in Discord Settings > Advanced > Developer Mode
2. Right-click on user/role/channel and select "Copy ID"

### Message Formatting Support
- **Bold**: `**text**`
- **Italic**: `*text*`
- **Code**: `` `code` ``
- **Code blocks**: ``` ```language\ncode\n``` ```
- **Underline**: `__text__`
- **Strikethrough**: `~~text~~`

### Next Steps for Users
1. Add additional Discord servers to test multi-server functionality
2. Integrate with MCP-compatible AI tools for Discord automation
3. Consider extending with user operations or search functionality as needed
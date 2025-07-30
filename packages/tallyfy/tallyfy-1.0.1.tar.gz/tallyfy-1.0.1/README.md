# MCP WebSocket Server

A WebSocket server that provides multi-user access to the MCP (Model Context Protocol) client for Tallyfy workflow automation.

## Features

- **Multi-user Support**: Multiple clients can connect simultaneously
- **Session Management**: Each connection gets its own conversation history
- **Real-time Communication**: WebSocket-based for instant responses
- **Shared MCP Client**: Single MCP client connection serves all users
- **Automatic Cleanup**: Inactive sessions are automatically cleaned up

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Clients   │    │  WebSocket      │    │   MCP Client    │
│   (Multiple)    │◄──►│     Server      │◄──►│   (Shared)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Session Manager │
                       │ (Per-user conv) │
                       └─────────────────┘
```

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up server environment variables**:
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   # Optional: Set default values (users will provide their own)
   export TALLYFY_API_KEY="fallback-api-key"  
   export TALLYFY_ORG_ID="fallback-org-id"
   ```

3. **Start the MCP server** (in separate terminal):
   ```bash
   python -m server.server
   ```

4. **Start the WebSocket server**:
   ```bash
   python run_websocket_server.py
   ```

5. **Connect and authenticate clients**:
   - Open `test_client.html` in a web browser
   - Connect to the WebSocket server
   - **Authenticate with your Tallyfy credentials** (API key + org ID)
   - Start sending queries

## Usage

### Web Interface

Open `test_client.html` in your browser for a ready-to-use chat interface.

### WebSocket API

Connect to `ws://localhost:8765` and send messages in JSON format:

```json
{
  "type": "query",
  "content": "Your message here"
}
```

#### Authentication

Before sending queries, users must authenticate with their Tallyfy credentials:

```json
{
  "type": "auth",
  "api_key": "your-tallyfy-api-key",
  "org_id": "your-organization-id"
}
```

#### Message Types

**Client to Server**:
- `auth`: Authenticate with API key and org ID
- `query`: Send a query to the MCP client
- `ping`: Ping the server

**Server to Client**:
- `connection_established`: Connection successful with session ID
- `auth_success`: Authentication successful
- `auth_error`: Authentication failed
- `response`: Response from the MCP client
- `processing`: Indicates query is being processed
- `info`: Informational messages
- `error`: Error messages
- `pong`: Response to ping

#### Special Commands

- `"clear"`: Clear conversation history
- `"quit"`: Disconnect from server

### Command Line Options

```bash
python run_websocket_server.py --help
```

Options:
- `--host`: Host to bind to (default: localhost)
- `--port`: Port to bind to (default: 8765)
- `--debug`: Enable debug logging

## Session Management

Each WebSocket connection gets:
- Unique session ID
- Separate conversation history  
- **Per-user authentication** with Tallyfy API credentials
- **Isolated credential storage** for secure multi-tenancy
- Automatic cleanup after 60 minutes of inactivity

## File Structure

```
client/
├── __init__.py              # Package initialization
├── config.py               # Configuration management
├── conversation.py         # Conversation history management
├── exceptions.py           # Custom exceptions
├── mcp_client.py          # Core MCP client logic
├── prompts.py             # System prompts
├── session_manager.py     # Multi-user session management
└── websocket_server.py    # WebSocket server implementation

websocket_server.py        # Server entry point
test_client.html          # Web-based test client
README.md                 # This file
```

## Development

### Running Tests

```bash
# Start the MCP server
python -m server.server

# Start the WebSocket server
python run_websocket_server.py --debug

# Open index.html in browser
```

### Adding Features

1. **New Message Types**: Add handlers in `websocket_server.py`
2. **Session Features**: Extend `session_manager.py`
3. **MCP Extensions**: Modify `mcp_client.py`

## Configuration

Environment variables:
- `ANTHROPIC_API_KEY`: Required for Claude API access
- `TALLYFY_API_KEY`: Required for Tallyfy API access
- `TALLYFY_ORG_ID`: Optional, auto-injected if provided
- `MCP_SERVER_URL`: Optional, defaults to `http://127.0.0.1:9000/mcp/`

## Monitoring

The server provides:
- Connection logging
- Session statistics
- Automatic cleanup of inactive sessions
- Health monitoring via ping/pong

## Error Handling

- Graceful handling of client disconnections
- Automatic session cleanup
- Comprehensive error logging
- Fallback responses for failed operations

## Security Considerations

- **Per-session authentication** with user-provided Tallyfy API credentials
- **Credential isolation** - each session stores its own API keys securely in memory
- **Session-based access control** - queries are authenticated with user's own credentials
- **No credential persistence** - API keys are only stored in memory during active sessions
- **Environment variables** for server configuration (Anthropic API key)
- **Input validation** on all WebSocket messages
- **Session timeout** - automatic cleanup of inactive sessions
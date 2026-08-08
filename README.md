# Discord MCP Server

Manage a Discord server directly from your AI coding assistant. Create channels, categories, roles, set permissions, assign roles, and more — all through natural language.

## Tools

| Tool | Description |
|---|---|
| `create_category` | Create a new category channel |
| `create_channel` | Create a text or voice channel under a category |
| `create_role` | Create a new role with color, hoist, mentionable |
| `edit_role` | Edit a role's name, color, hoist, or mentionable |
| `delete_role` | Delete a role (non-managed, below bot's hierarchy) |
| `assign_role` | Assign a role to a member by username |
| `remove_role` | Remove a role from a member by username |
| `restrict_channel` | Set channel permissions (allow/deny roles, read-only mode, thread control) |
| `create_role_restricted_channel` | Create a channel + restrict it in one call |
| `rename_channel` | Rename a text or voice channel |
| `delete_category` | Delete a category channel |
| `delete_channel` | Delete a text or voice channel |
| `list_channels` | List all channels with their names, types, and categories |
| `list_roles` | List all roles with their names, colors, and member counts |
| `create_webhook` | Create a webhook in a text channel |
| `send_webhook_message` | Send a message through an existing webhook |
| `set_slowmode` | Set the slowmode delay (seconds) on a text channel |

## Setup

### 1. Create a Discord bot

1. Go to https://discord.com/developers/applications
2. Click **New Application** → name it → **Create**
3. Go to **Bot** → **Add Bot**
4. Under **Privileged Gateway Intents**, enable:
   - `Server Members Intent`
   - `Message Content Intent`
5. Copy the **Token**
6. Go to **OAuth2** → **URL Generator**
   - Scopes: `bot`
   - Bot Permissions: `Administrator` (or manually select: Manage Channels, Manage Roles, Kick Members, Manage Webhooks, Send Messages, Read Messages, View Channels)
7. Open the generated URL in your browser to invite the bot to your server

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and paste your bot token:

```
DISCORD_TOKEN=your_token_here
```

Optional: pin the bot to a specific server by name (defaults to `Monolith`). All tools operate on this guild only:

```
DISCORD_GUILD_NAME=Monolith
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## MCP Host Configuration

### opencode

Add to `opencode.json` in your project root:

```json
{
  "mcp": {
    "discord": {
      "type": "local",
      "command": ["python", "/absolute/path/to/discord_mcp_server.py"]
    }
  }
}
```

Restart opencode to load the server.

### Claude Desktop

Edit `claude_desktop_config.json` (File → Settings → Developer → Edit Config):

```json
{
  "mcpServers": {
    "discord": {
      "command": "python",
      "args": ["/absolute/path/to/discord_mcp_server.py"],
      "env": {
        "DISCORD_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Claude Code

Add to `~/.claude.json` or `.mcp.json` in your project:

```json
{
  "mcpServers": {
    "discord": {
      "command": "python",
      "args": ["/absolute/path/to/discord_mcp_server.py"],
      "env": {
        "DISCORD_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Cursor

Create `.cursor/mcp.json` in your project root (or `~/.cursor/mcp.json` for global):

```json
{
  "mcpServers": {
    "discord": {
      "command": "python",
      "args": ["/absolute/path/to/discord_mcp_server.py"],
      "env": {
        "DISCORD_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "discord": {
      "command": "python",
      "args": ["/absolute/path/to/discord_mcp_server.py"],
      "env": {
        "DISCORD_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Codex CLI

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.discord]
command = "python"
args = ["/absolute/path/to/discord_mcp_server.py"]

[mcp_servers.discord.env]
DISCORD_TOKEN = "your_token_here"
```

Or add via CLI:

```bash
codex mcp add discord -- python /absolute/path/to/discord_mcp_server.py
```

### Antigravity (Google)

Add to `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "discord": {
      "command": "python",
      "args": ["C:\\path\\to\\discord_mcp_server.py"],
      "env": {
        "DISCORD_TOKEN": "your_token_here"
      }
    }
  }
}
```

Open Antigravity → Agent panel → `...` → MCP Servers → Manage MCP Servers → View raw config.

> **Note:** If using the `.env` file instead of inline `env`, omit the `env` block and ensure `load_dotenv()` in the script finds your `.env` (the working directory depends on the host).

## How it works

The script runs an MCP server over stdio that connects to Discord via the bot token. It registers all tools on startup, and your AI assistant calls them as needed. The Discord bot only needs to be in **one server** — it auto-selects the first guild on login.

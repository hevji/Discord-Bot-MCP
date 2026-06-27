# Agent Guide: Discord MCP Server

This project hosts a Discord bot behind an MCP server. When the MCP server is running, you (the AI agent) can call its tools to manage the Discord server directly.

## Prerequisites

- Python 3.11+ with `discord.py`, `mcp`, and `python-dotenv` installed
- A `.env` file with `DISCORD_TOKEN=<bot_token>`
- The bot must be invited to the Discord server with **Administrator** permissions (or at minimum: Manage Channels, Manage Roles, Kick Members, Manage Webhooks, Read Messages, Send Messages)

## How to connect

The MCP server is already configured in `opencode.json` as a local MCP server. It starts automatically when opencode launches. If you cannot see the Discord tools (`create_category`, `create_channel`, etc.), the server may not be running.

### If tools are missing

Check whether the MCP server is connected:

1. Ensure `.env` has a valid `DISCORD_TOKEN`
2. Restart opencode so it reloads `opencode.json` and spawns the MCP server
3. If the token is expired or invalid, ask the user to generate a new one at https://discord.com/developers/applications

## Tool overview

| Tool | When to use |
|---|---|
| `create_category` | Create a category channel (e.g. "INFORMATION", "COMMUNITY") |
| `create_channel` | Create a text/voice channel under a parent category |
| `create_role` | Create a new role (supports `color`, `hoist`, `mentionable`) |
| `edit_role` | Change a role's name, color, or hoist status |
| `delete_role` | Remove a role (fails if managed, @everyone, or above the bot) |
| `assign_role` | Give a role to a member by username |
| `remove_role` | Take a role from a member by username |
| `restrict_channel` | Set channel-level permissions — allow/deny roles, toggle read-only with `send_messages` |
| `create_role_restricted_channel` | Create a text channel and apply role restrictions in one call |
| `delete_category` | Remove a category (cascade-deletes child channels) |
| `delete_channel` | Remove a single text/voice channel |

## Permission model patterns

The most common setup pattern used in this server is **role-based channel gating**:

- **Members** role: allowed on all public channels, denied on staff/verify channels
- **Unverified** role: allowed only on `#verify`, denied everywhere else
- **@everyone**: denied on most channels (access is granted only via explicit roles)

When setting up read-only channels (like `#rules`, `#announcements`), pass `send_messages=false` to `restrict_channel`.

## Notes

- The bot auto-selects the **first guild** it's in. If it's in multiple servers, only the first one is manageable.
- Managed roles (created by bot integrations like RaidProtect, Ticket Tool, etc.) cannot be deleted through the API.
- Roles above the bot's highest role in the hierarchy cannot be deleted or edited.
- Member lookup uses `fetch_members()` with a limit of 100 — works for most servers.

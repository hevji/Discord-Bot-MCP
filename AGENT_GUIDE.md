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

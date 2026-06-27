"""
Discord Bot MCP Server

Provides MCP tools to manage a Discord server:
- Create categories, channels (text/voice), roles
- Restrict channel access to specific roles via permission overwrites
"""

import os
import asyncio
import logging
from typing import Optional

import discord
from discord import Intents, PermissionOverwrite, ChannelType
from discord.ext import commands
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from mcp.types import ServerCapabilities, ToolsCapability

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord-mcp")

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required")

intents = Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
mcp_server = Server("discord-bot")

guild: Optional[discord.Guild] = None
bot_ready = asyncio.Event()


@bot.event
async def on_ready():
    global guild
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    if bot.guilds:
        guild = bot.guilds[0]
        logger.info(f"Connected to guild: {guild.name} (ID: {guild.id})")
        bot_ready.set()
    else:
        logger.warning("Bot is not in any guild. Invite it to a server first.")


@mcp_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="create_category",
            description="Create a new category channel in the Discord server",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the category to create",
                    },
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="create_channel",
            description="Create a text or voice channel under a specific category",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the channel to create",
                    },
                    "category_name": {
                        "type": "string",
                        "description": "Name of the parent category",
                    },
                    "channel_type": {
                        "type": "string",
                        "enum": ["text", "voice"],
                        "description": "Type of channel (default: text)",
                    },
                    "topic": {
                        "type": "string",
                        "description": "Topic for text channels",
                    },
                },
                "required": ["name", "category_name"],
            },
        ),
        types.Tool(
            name="create_role",
            description="Create a new role in the Discord server",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the role to create",
                    },
                    "color": {
                        "type": "string",
                        "description": "Hex color for the role, e.g. #FF0000",
                    },
                    "hoist": {
                        "type": "boolean",
                        "description": "Show role members separately in the sidebar",
                    },
                    "mentionable": {
                        "type": "boolean",
                        "description": "Allow anyone to @mention this role",
                    },
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="restrict_channel",
            description=(
                "Restrict channel access to specific roles. "
                "Denies @everyone read access and grants it only to specified roles. "
                "Use this to create private channels."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_name": {
                        "type": "string",
                        "description": "Name of the channel to restrict",
                    },
                    "allowed_role_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of role names that should have access",
                    },
                    "denied_role_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of role names to explicitly deny access to",
                    },
                    "deny_everyone": {
                        "type": "boolean",
                        "description": "Deny @everyone access (default: true)",
                    },
                    "send_messages": {
                        "type": "boolean",
                        "description": "Allow allowed roles to send messages (default: true). Set false for read-only channels.",
                    },
                },
                "required": ["channel_name", "allowed_role_names"],
            },
        ),
        types.Tool(
            name="create_role_restricted_channel",
            description=(
                "Create a new text channel under a category and immediately restrict "
                "its access to one or more roles. Combines create_channel + restrict_channel "
                "in a single call."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the channel to create",
                    },
                    "category_name": {
                        "type": "string",
                        "description": "Name of the parent category",
                    },
                    "allowed_role_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Roles that should have access to this channel",
                    },
                    "denied_role_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Roles to explicitly deny access to",
                    },
                    "topic": {
                        "type": "string",
                        "description": "Topic for the channel",
                    },
                },
                "required": ["name", "category_name"],
            },
        ),
        types.Tool(
            name="delete_category",
            description="Delete a category channel by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the category to delete",
                    },
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="delete_channel",
            description="Delete a text or voice channel by name",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the channel to delete",
                    },
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="assign_role",
            description="Assign a role to a member by their username",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username of the member",
                    },
                    "role_name": {
                        "type": "string",
                        "description": "Name of the role to assign",
                    },
                },
                "required": ["username", "role_name"],
            },
        ),
        types.Tool(
            name="remove_role",
            description="Remove a role from a member by their username",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username of the member",
                    },
                    "role_name": {
                        "type": "string",
                        "description": "Name of the role to remove",
                    },
                },
                "required": ["username", "role_name"],
            },
        ),
        types.Tool(
            name="edit_role",
            description="Edit an existing role's name, color, hoist, or mentionable settings",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Current name of the role to edit",
                    },
                    "new_name": {
                        "type": "string",
                        "description": "New name for the role",
                    },
                    "color": {
                        "type": "string",
                        "description": "Hex color for the role, e.g. #FF0000",
                    },
                    "hoist": {
                        "type": "boolean",
                        "description": "Show role members separately in the sidebar",
                    },
                    "mentionable": {
                        "type": "boolean",
                        "description": "Allow anyone to @mention this role",
                    },
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="delete_role",
            description="Delete a role by name (cannot delete @everyone, managed roles, or roles above the bot)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the role to delete",
                    },
                },
                "required": ["name"],
            },
        ),
    ]


async def ensure_guild() -> discord.Guild:
    global guild
    if guild is None:
        await asyncio.wait_for(bot_ready.wait(), timeout=30.0)
    return guild


@mcp_server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    g = await ensure_guild()
    args = arguments or {}

    try:
        if name == "create_category":
            return await _create_category(g, args)
        elif name == "create_channel":
            return await _create_channel(g, args)
        elif name == "create_role":
            return await _create_role(g, args)
        elif name == "restrict_channel":
            return await _restrict_channel(g, args)
        elif name == "create_role_restricted_channel":
            return await _create_role_restricted_channel(g, args)
        elif name == "assign_role":
            return await _assign_role(g, args)
        elif name == "remove_role":
            return await _remove_role(g, args)
        elif name == "edit_role":
            return await _edit_role(g, args)
        elif name == "delete_category":
            return await _delete_category(g, args)
        elif name == "delete_channel":
            return await _delete_channel(g, args)
        elif name == "delete_role":
            return await _delete_role(g, args)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.exception(f"Error executing tool {name}")
        return [types.TextContent(type="text", text=f"Error: {e}")]


async def _create_category(g: discord.Guild, args: dict) -> list[types.TextContent]:
    name = args["name"]
    existing = discord.utils.get(g.categories, name=name)
    if existing:
        return [
            types.TextContent(
                type="text",
                text=f"Category '{name}' already exists (ID: {existing.id})",
            )
        ]
    category = await g.create_category(name, reason="Created via MCP")
    return [
        types.TextContent(
            type="text",
            text=f"Created category '{category.name}' (ID: {category.id})",
        )
    ]


async def _create_channel(g: discord.Guild, args: dict) -> list[types.TextContent]:
    channel_name = args["name"]
    category_name = args["category_name"]
    channel_type = args.get("channel_type", "text")
    topic = args.get("topic", "")

    category = discord.utils.get(g.categories, name=category_name)
    if not category:
        return [
            types.TextContent(
                type="text", text=f"Category '{category_name}' not found"
            )
        ]

    existing = discord.utils.get(category.channels, name=channel_name)
    if existing:
        return [
            types.TextContent(
                type="text",
                text=f"Channel '{channel_name}' already exists (ID: {existing.id})",
            )
        ]

    if channel_type == "voice":
        channel = await g.create_voice_channel(
            channel_name, category=category, reason="Created via MCP"
        )
    else:
        channel = await g.create_text_channel(
            channel_name, category=category, topic=topic, reason="Created via MCP"
        )

    return [
        types.TextContent(
            type="text",
            text=f"Created {channel_type} channel '{channel.name}' (ID: {channel.id})",
        )
    ]


async def _create_role(g: discord.Guild, args: dict) -> list[types.TextContent]:
    role_name = args["name"]
    color_hex = args.get("color")
    hoist = args.get("hoist", False)
    mentionable = args.get("mentionable", False)

    existing = discord.utils.get(g.roles, name=role_name)
    if existing:
        return [
            types.TextContent(
                type="text",
                text=f"Role '{role_name}' already exists (ID: {existing.id})",
            )
        ]

    colour = discord.Colour.default()
    if color_hex:
        colour = discord.Colour.from_str(color_hex)

    role = await g.create_role(
        name=role_name,
        colour=colour,
        hoist=hoist,
        mentionable=mentionable,
        reason="Created via MCP",
    )

    return [
        types.TextContent(
            type="text",
            text=f"Created role '{role.name}' (ID: {role.id}, color: {role.colour})",
        )
    ]


async def _restrict_channel(
    g: discord.Guild, args: dict
) -> list[types.TextContent]:
    channel_name = args["channel_name"]
    allowed_role_names = args["allowed_role_names"]
    denied_role_names = args.get("denied_role_names", [])
    deny_everyone = args.get("deny_everyone", True)
    send_messages = args.get("send_messages", True)

    channel = discord.utils.get(g.channels, name=channel_name)
    if not channel:
        return [
            types.TextContent(
                type="text", text=f"Channel '{channel_name}' not found"
            )
        ]

    allowed_roles = []
    for rn in allowed_role_names:
        role = discord.utils.get(g.roles, name=rn)
        if not role:
            return [
                types.TextContent(
                    type="text", text=f"Role '{rn}' not found"
                )
            ]
        allowed_roles.append(role)

    denied_roles = []
    for rn in denied_role_names:
        role = discord.utils.get(g.roles, name=rn)
        if not role:
            return [
                types.TextContent(
                    type="text", text=f"Role '{rn}' not found"
                )
            ]
        denied_roles.append(role)

    overwrites = {}

    if deny_everyone:
        overwrites[g.default_role] = PermissionOverwrite(
            read_messages=False,
            view_channel=False,
            send_messages=False,
            connect=False,
        )

    for role in allowed_roles:
        overwrites[role] = PermissionOverwrite(
            read_messages=True,
            view_channel=True,
            send_messages=send_messages,
            connect=send_messages,
            speak=send_messages,
        )

    for role in denied_roles:
        overwrites[role] = PermissionOverwrite(
            read_messages=False,
            view_channel=False,
            send_messages=False,
            connect=False,
            speak=False,
        )

    await channel.edit(overwrites=overwrites, reason="Restricted via MCP")

    parts = []
    if allowed_roles:
        parts.append(f"allowed: {', '.join(r.name for r in allowed_roles)}")
    if denied_roles:
        parts.append(f"denied: {', '.join(r.name for r in denied_roles)}")
    if deny_everyone:
        parts.append("@everyone denied")

    return [
        types.TextContent(
            type="text",
            text=f"Restricted channel '{channel_name}' — {'; '.join(parts)}",
        )
    ]


async def _create_role_restricted_channel(
    g: discord.Guild, args: dict
) -> list[types.TextContent]:
    channel_name = args["name"]
    category_name = args["category_name"]
    allowed_role_names = args.get("allowed_role_names", [])
    denied_role_names = args.get("denied_role_names", [])
    topic = args.get("topic", "")

    category = discord.utils.get(g.categories, name=category_name)
    if not category:
        return [
            types.TextContent(
                type="text", text=f"Category '{category_name}' not found"
            )
        ]

    allowed_roles = []
    for rn in allowed_role_names:
        role = discord.utils.get(g.roles, name=rn)
        if not role:
            return [
                types.TextContent(
                    type="text", text=f"Role '{rn}' not found"
                )
            ]
        allowed_roles.append(role)

    denied_roles = []
    for rn in denied_role_names:
        role = discord.utils.get(g.roles, name=rn)
        if not role:
            return [
                types.TextContent(
                    type="text", text=f"Role '{rn}' not found"
                )
            ]
        denied_roles.append(role)

    existing = discord.utils.get(category.channels, name=channel_name)
    if existing:
        return [
            types.TextContent(
                type="text",
                text=f"Channel '{channel_name}' already exists (ID: {existing.id})",
            )
        ]

    overwrites = {
        g.default_role: PermissionOverwrite(
            read_messages=False,
            view_channel=False,
            send_messages=False,
        ),
    }
    for role in allowed_roles:
        overwrites[role] = PermissionOverwrite(
            read_messages=True,
            view_channel=True,
            send_messages=True,
        )
    for role in denied_roles:
        overwrites[role] = PermissionOverwrite(
            read_messages=False,
            view_channel=False,
            send_messages=False,
        )

    channel = await g.create_text_channel(
        channel_name,
        category=category,
        topic=topic,
        overwrites=overwrites,
        reason="Created and restricted via MCP",
    )

    parts = []
    if allowed_roles:
        parts.append(f"allowed: {', '.join(r.name for r in allowed_roles)}")
    if denied_roles:
        parts.append(f"denied: {', '.join(r.name for r in denied_roles)}")

    return [
        types.TextContent(
            type="text",
            text=(
                f"Created restricted text channel '{channel.name}' (ID: {channel.id}) "
                f"under '{category_name}' — {'; '.join(parts)}"
            ),
        )
    ]


async def _edit_role(g: discord.Guild, args: dict) -> list[types.TextContent]:
    role_name = args["name"]
    role = discord.utils.get(g.roles, name=role_name)
    if not role:
        return [types.TextContent(type="text", text=f"Role '{role_name}' not found")]
    if role.managed:
        return [types.TextContent(type="text", text=f"Role '{role_name}' is managed and cannot be edited")]

    kwargs = {}
    if "new_name" in args:
        kwargs["name"] = args["new_name"]
    if "color" in args:
        kwargs["colour"] = discord.Colour.from_str(args["color"])
    if "hoist" in args:
        kwargs["hoist"] = args["hoist"]
    if "mentionable" in args:
        kwargs["mentionable"] = args["mentionable"]

    if not kwargs:
        return [types.TextContent(type="text", text=f"No changes specified for role '{role_name}'")]

    await role.edit(**kwargs, reason="Edited via MCP")

    changed = ", ".join(kwargs.keys())
    return [types.TextContent(type="text", text=f"Edited role '{role_name}': {changed}")]


async def _delete_category(g: discord.Guild, args: dict) -> list[types.TextContent]:
    name = args["name"]
    cat = discord.utils.get(g.categories, name=name)
    if not cat:
        return [types.TextContent(type="text", text=f"Category '{name}' not found")]
    await cat.delete()
    return [types.TextContent(type="text", text=f"Deleted category '{name}'")]


async def _delete_channel(g: discord.Guild, args: dict) -> list[types.TextContent]:
    name = args["name"]
    channel = discord.utils.get(g.channels, name=name)
    if not channel:
        return [types.TextContent(type="text", text=f"Channel '{name}' not found")]
    await channel.delete()
    return [types.TextContent(type="text", text=f"Deleted channel '{name}'")]


async def _delete_role(g: discord.Guild, args: dict) -> list[types.TextContent]:
    role_name = args["name"]
    role = discord.utils.get(g.roles, name=role_name)
    if not role:
        return [types.TextContent(type="text", text=f"Role '{role_name}' not found")]
    if role.is_default():
        return [types.TextContent(type="text", text=f"Cannot delete @everyone role")]
    if role.managed:
        return [types.TextContent(type="text", text=f"Role '{role_name}' is managed by an integration and cannot be deleted")]
    if role >= g.me.top_role:
        return [types.TextContent(type="text", text=f"Role '{role_name}' is at or above the bot's highest role and cannot be deleted")]
    await role.delete()
    return [types.TextContent(type="text", text=f"Deleted role '{role_name}'")]


async def _assign_role(g: discord.Guild, args: dict) -> list[types.TextContent]:
    username = args["username"]
    role_name = args["role_name"]

    role = discord.utils.get(g.roles, name=role_name)
    if not role:
        return [types.TextContent(type="text", text=f"Role '{role_name}' not found")]

    members = [m async for m in g.fetch_members(limit=100)]
    member = discord.utils.get(members, name=username)
    if not member:
        return [types.TextContent(type="text", text=f"Member '{username}' not found")]

    await member.add_roles(role, reason="Assigned via MCP")
    return [types.TextContent(type="text", text=f"Assigned role '{role_name}' to {username}")]


async def _remove_role(g: discord.Guild, args: dict) -> list[types.TextContent]:
    username = args["username"]
    role_name = args["role_name"]

    role = discord.utils.get(g.roles, name=role_name)
    if not role:
        return [types.TextContent(type="text", text=f"Role '{role_name}' not found")]

    members = [m async for m in g.fetch_members(limit=100)]
    member = discord.utils.get(members, name=username)
    if not member:
        return [types.TextContent(type="text", text=f"Member '{username}' not found")]

    await member.remove_roles(role, reason="Removed via MCP")
    return [types.TextContent(type="text", text=f"Removed role '{role_name}' from {username}")]


async def run_mcp_server():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="discord-bot",
                server_version="0.1.0",
                capabilities=ServerCapabilities(
                    tools=ToolsCapability(listChanged=False)
                ),
            ),
        )


async def main():
    tasks = [
        asyncio.create_task(bot.start(DISCORD_TOKEN)),
        asyncio.create_task(run_mcp_server()),
    ]

    done, pending = await asyncio.wait(
        tasks, return_when=asyncio.FIRST_COMPLETED
    )

    for task in pending:
        task.cancel()

    await asyncio.gather(*pending, return_exceptions=True)

    await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")

"""MCP Time Server for providing time-related tools."""

import json
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from enum import Enum
from zoneinfo import ZoneInfo

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError
from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool
from pydantic import BaseModel
from tzlocal import get_localzone


class TimeTools(str, Enum):
    """Enum for available time tools."""

    GET_CURRENT_TIME = "get_current_time"
    CONVERT_TIME = "convert_time"


class TimeResult(BaseModel):
    """Represents the result of a time query."""

    timezone: str
    datetime: str
    is_dst: bool


class TimeConversionResult(BaseModel):
    """Represents the result of a time conversion."""

    source: TimeResult
    target: TimeResult
    time_difference: str


class TimeConversionInput(BaseModel):
    """Represents the input for time conversion."""

    source_tz: str
    time: str
    target_tz_list: list[str]


def get_local_tz(local_tz_override: str | None = None) -> ZoneInfo:
    """
    Get the local timezone.

    Args:
        local_tz_override: Optional timezone string to override local detection.

    Returns:
        A ZoneInfo object representing the local timezone.

    Raises:
        McpError: If the local timezone cannot be determined.

    """
    if local_tz_override:
        return ZoneInfo(local_tz_override)

    # Get local timezone using tzlocal
    try:
        return get_localzone()
    except Exception as exception:
        message = f"Could not determine local timezone: {exception!s}"
        raise McpError(message) from exception


def get_zoneinfo(timezone_name: str) -> ZoneInfo:
    """
    Get a ZoneInfo object for a given timezone name.

    Args:
        timezone_name: The IANA timezone name (e.g., 'America/New_York').

    Returns:
        A ZoneInfo object.

    Raises:
        McpError: If the timezone name is invalid.

    """
    try:
        return ZoneInfo(timezone_name)
    except Exception as exception:
        message = f"Invalid timezone: {exception!s}"
        raise McpError(message) from exception


class TimeServer:
    """Provides methods for time-related operations."""

    def get_current_time(self, timezone_name: str) -> TimeResult:
        """Get current time in specified timezone."""
        timezone = get_zoneinfo(timezone_name)
        current_time = datetime.now(timezone)

        return TimeResult(
            timezone=timezone_name,
            datetime=current_time.isoformat(timespec="seconds"),
            is_dst=bool(current_time.dst()),
        )

    def convert_time(
        self,
        source_tz: str,
        time_str: str,
        target_tz: str,
    ) -> TimeConversionResult:
        """Convert time between timezones."""
        source_timezone = get_zoneinfo(source_tz)
        target_timezone = get_zoneinfo(target_tz)

        try:
            parsed_time = datetime.strptime(time_str, "%H:%M").astimezone(UTC).time()
        except ValueError as error:
            message = "Invalid time format. Expected HH:MM [24-hour format]"
            raise ValueError(message) from error

        now = datetime.now(source_timezone)
        source_time = datetime(
            now.year,
            now.month,
            now.day,
            parsed_time.hour,
            parsed_time.minute,
            tzinfo=source_timezone,
        )

        target_time = source_time.astimezone(target_timezone)
        source_offset = source_time.utcoffset() or timedelta()
        target_offset = target_time.utcoffset() or timedelta()
        hours_difference = (target_offset - source_offset).total_seconds() / 3600

        if hours_difference.is_integer():
            time_diff_str = f"{hours_difference:+.1f}h"
        else:
            # For fractional hours like Nepal's UTC+5:45
            time_diff_str = f"{hours_difference:+.2f}".rstrip("0").rstrip(".") + "h"

        return TimeConversionResult(
            source=TimeResult(
                timezone=source_tz,
                datetime=source_time.isoformat(timespec="seconds"),
                is_dst=bool(source_time.dst()),
            ),
            target=TimeResult(
                timezone=target_tz,
                datetime=target_time.isoformat(timespec="seconds"),
                is_dst=bool(target_time.dst()),
            ),
            time_difference=time_diff_str,
        )


async def serve(local_timezone: str | None = None) -> None:
    """
    Serve the MCP Time Server.

    Args:
        local_timezone: Optional timezone string to use as the local timezone.

    """
    server = Server("mcp-time")
    time_server = TimeServer()
    local_tz = str(get_local_tz(local_timezone))

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available time tools."""
        return [
            Tool(
                name=TimeTools.GET_CURRENT_TIME.value,
                description="Get current time in a specific timezones",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": (
                                "IANA timezone name (e.g., 'America/New_York', "
                                f"'Europe/London'). Use '{local_tz}' as local timezone "
                                "if no timezone provided by the user.",
                            ),
                        },
                    },
                    "required": ["timezone"],
                },
            ),
            Tool(
                name=TimeTools.CONVERT_TIME.value,
                description="Convert time between timezones",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source_timezone": {
                            "type": "string",
                            "description": (
                                "Source IANA timezone name (e.g., 'America/New_York', "
                                f"'Europe/London'). Use '{local_tz}' as local timezone "
                                "if no source timezone provided by the user.",
                            ),
                        },
                        "time": {
                            "type": "string",
                            "description": "Time to convert in 24-hour format (HH:MM)",
                        },
                        "target_timezone": {
                            "type": "string",
                            "description": (
                                "Target IANA timezone name (e.g., 'Asia/Tokyo', "
                                f"'America/San_Francisco'). Use '{local_tz}' as local "
                                "timezone if no target timezone provided by the user.",
                            ),
                        },
                    },
                    "required": ["source_timezone", "time", "target_timezone"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(
        name: str,
        arguments: dict,
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls for time queries."""
        match name:
            case TimeTools.GET_CURRENT_TIME.value:
                timezone = arguments.get("timezone")
                if not timezone:
                    message = "Missing required argument: timezone"
                    raise ValueError(message)

                result = time_server.get_current_time(timezone)

            case TimeTools.CONVERT_TIME.value:
                if not all(
                    k in arguments
                    for k in ["source_timezone", "time", "target_timezone"]
                ):
                    message = "Missing required arguments"
                    raise ValueError(message)

                result = time_server.convert_time(
                    arguments["source_timezone"],
                    arguments["time"],
                    arguments["target_timezone"],
                )
            case _:
                message = f"Unknown tool: {name}"
                raise ValueError(message)

        return [
            TextContent(
                type="text",
                text=json.dumps(result.model_dump(), indent=2),
            ),
        ]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)

# agentpipe/__init__.py
import logging

from .tasks import instruct, parallel, route, loop
from .tools import tool

# Expose key formatters directly if desired
from .format import to_json, from_xml, passthrough, from_markdown_code, is_tool_call

# Set up the library's logger to use a NullHandler.
# This ensures that log messages from agentpipe don't appear unless
# the application consuming the library has configured logging.
logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "instruct",
    "parallel",
    "route",
    "loop",
    "tool",
    "to_json",
    "from_xml",
    "passthrough",
    "from_markdown_code",
    "is_tool_call",
]
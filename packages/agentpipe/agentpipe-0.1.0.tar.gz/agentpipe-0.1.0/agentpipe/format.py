import json
import re
from .runnable import Runnable
from .context import PipeContext

class ToJson(Runnable):
    def __repr__(self) -> str:
        return "to_json()"

    def _invoke(self, context: PipeContext) -> PipeContext:
        # Assumes pipe_value is a JSON string
        context.pipe_value = json.loads(str(context.pipe_value))
        return context

def to_json() -> Runnable:
    return ToJson()

class FromXml(Runnable):
    def __init__(self, tag: str):
        super().__init__()
        self.tag = tag

    def __repr__(self) -> str:
        return f"from_xml('{self.tag}')"

    def _invoke(self, context: PipeContext) -> PipeContext:
        # Uses regex to find content within a tag, robust to malformed XML/markdown.
        text = str(context.pipe_value)
        # Pattern to non-greedily find content between <tag> and </tag> across newlines.
        # It's case-insensitive to handle tags like <Answer> or <ANSWER>.
        pattern = f"<{re.escape(self.tag)}>(.*?)</{re.escape(self.tag)}>"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

        if match:
            # Extract content from the first capturing group and strip whitespace.
            context.pipe_value = match.group(1).strip()
        else:
            context.pipe_value = None
        return context

def from_xml(tag: str) -> Runnable:
    return FromXml(tag)


class FromMarkdownCode(Runnable):
    def __init__(self, language: str):
        super().__init__()
        self.language = language

    def __repr__(self) -> str:
        return f"from_markdown_code('{self.language}')"

    def _invoke(self, context: PipeContext) -> PipeContext:
        text = str(context.pipe_value)
        # Pattern to find ```language ... ```
        # e.g., ```json ... ```
        pattern = f"```{re.escape(self.language)}\\s*([\\s\\S]+?)\\s*```"
        match = re.search(pattern, text)

        if match:
            # Extract content from the first capturing group and strip whitespace.
            context.pipe_value = match.group(1).strip()
        else:
            context.pipe_value = None
        return context


def from_markdown_code(language: str) -> Runnable:
    """
    Returns a Runnable that extracts text from a markdown code block with a
    specific language tag.

    e.g., `from_markdown_code("json")` will extract from ```json ... ```.
    """
    return FromMarkdownCode(language)


class Passthrough(Runnable):
    def __repr__(self) -> str:
        return "passthrough()"

    def _invoke(self, context: PipeContext) -> PipeContext:
        # Does nothing to the pipe_value
        return context

def passthrough() -> Runnable:
    return Passthrough()


class IsToolCall(Runnable):
    def __repr__(self) -> str:
        return "is_tool_call()"

    def _invoke(self, context: PipeContext) -> PipeContext:
        val = context.pipe_value
        is_call = isinstance(val, dict) and 'name' in val and 'arguments' in val
        context.pipe_value = is_call
        return context


def is_tool_call() -> Runnable:
    """
    Returns a Runnable that checks if the current pipe_value is a tool call.

    A tool call is identified as a dictionary containing 'name' and 'arguments' keys.
    This is useful as a condition for a `loop()` to create an agent.
    The runnable's output is either `True` or `False`.
    """
    return IsToolCall()
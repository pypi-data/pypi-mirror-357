import logging
import inspect
from typing import Callable, Any, Dict, Optional

from .runnable import Runnable
from .context import PipeContext

logger = logging.getLogger(__name__)

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = None


class Tool(Runnable):
    """A Runnable that wraps a Python function, making it usable in a workflow."""

    def __repr__(self) -> str:
        return f"tool(name='{self.func.__name__}')"

    def __init__(self, func: Callable, json_schema: Dict[str, Any], pydantic_model: Optional[type] = None):
        super().__init__()
        self.func = func
        self.json_schema = json_schema
        self.pydantic_model = pydantic_model
        # Make the Tool instance look like the original function
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def _invoke(self, context: PipeContext) -> PipeContext:
        """
        Executes the wrapped function.
        It expects `pipe_value` to be a dictionary of arguments.
        If a pydantic model is used, it instantiates it.
        """
        args = context.pipe_value
        logger.info(f"Executing tool '{self.func.__name__}' with arguments: {args!r}")
        
        if self.pydantic_model and isinstance(args, dict):
            model_instance = self.pydantic_model(**args)
            result = self.func(model_instance)
        elif isinstance(args, dict):
            result = self.func(**args)
        else:
            result = self.func(args)
        
        context.pipe_value = result
        return context

    def to_json(self) -> Dict[str, Any]:
        """Returns the JSON schema representation of the tool."""
        return self.json_schema


def tool(func: Callable) -> Tool:
    """
    Decorator to turn a Python function into a agentpipe Tool.

    It inspects the function's signature to generate a JSON schema that
    LLMs can use to understand how to call the function. It supports
    primitive types and Pydantic models for argument definitions.
    """
    sig = inspect.signature(func)
    docstring = inspect.getdoc(func) or ""

    pydantic_model = None
    if BaseModel:
        for param in sig.parameters.values():
            # Check if param.annotation is a class and a subclass of BaseModel
            if inspect.isclass(param.annotation) and issubclass(param.annotation, BaseModel):
                pydantic_model = param.annotation
                # Find the first one and use it as the source of truth for args.
                break
    
    if pydantic_model:
        # Pydantic model found, use it to generate schema
        schema = pydantic_model.model_json_schema()
        parameters = {
            "type": "object",
            "properties": schema.get("properties", {}),
            "required": schema.get("required", []),
        }
    else:
        # Fallback to original simple logic for non-pydantic functions
        type_map = {'str': 'string', 'int': 'integer', 'float': 'number', 'bool': 'boolean', 'Any': 'string'}
        properties = {}
        required = []
        for name, param in sig.parameters.items():
            param_type_name = getattr(param.annotation, '__name__', 'Any')
            param_type = type_map.get(param_type_name.lower(), 'string')
            properties[name] = {'type': param_type}
            if param.default == inspect.Parameter.empty:
                required.append(name)
        parameters = {"type": "object", "properties": properties, "required": required}

    tool_schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": docstring.split('\n')[0],
            "parameters": parameters,
        }
    }
    
    return Tool(func, tool_schema, pydantic_model=pydantic_model)
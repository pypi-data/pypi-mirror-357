import copy
from typing import Any, Dict, List

class PipeContext:
    """Internal class to hold and pass state through a pipe."""
    def __init__(self, initial_input: Any = None):
        self.state: Dict[str, Any] = {}
        self.pipe_value: Any = None
        self.history: List[Dict[str, Any]] = []

        if isinstance(initial_input, dict):
            self.state.update(initial_input)
            if "input" in initial_input:
                self.pipe_value = initial_input["input"]
        else:
            self.pipe_value = initial_input
    
    def get_format_context(self) -> Dict[str, Any]:
        """Returns the combined context for formatting prompts."""
        ctx = self.state.copy()
        ctx["input"] = self.pipe_value
        return ctx

    def copy(self) -> 'PipeContext':
        """
        Creates a copy of the context.
        The state is deep-copied to ensure isolation for mutable objects.
        """
        new_context = PipeContext()
        new_context.state = copy.deepcopy(self.state)
        new_context.pipe_value = self.pipe_value
        # The history is also copied so branches start from the same point.
        new_context.history = self.history.copy()
        return new_context
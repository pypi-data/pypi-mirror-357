import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Union

from .context import PipeContext

logger = logging.getLogger(__name__)


class PipeResult:
    """
    A special result object that contains the final output of a pipe,
    its final state, and a complete history of all intermediate steps.
    """
    def __init__(self, final_output: Any, state: Dict[str, Any], history: List[Dict[str, Any]]):
        self.final_output = final_output
        self.state = state
        self.history = history

    def __str__(self) -> str:
        """Behaves like the final output when printed."""
        return str(self.final_output)

    def __repr__(self) -> str:
        """Provides a detailed representation of the result object."""
        return (
            f"PipeResult(final_output={self.final_output!r}, "
            f"state_keys={list(self.state.keys())}, history_steps={len(self.history)})"
        )
    
    def print_history(self):
        """Prints a human-readable trace of the pipe execution."""
        print("--- Pipe Execution History ---")
        if not self.history:
            print("No steps were recorded.")
        for i, step in enumerate(self.history):
            print(f"\n[Step {i+1}: {step['name']}]")
            if "saved_as" in step:
                print(f"  - Saved output to state as '{step['saved_as']}'")
            print(f"  Input:  {step['input']!r}")
            print(f"  Output: {step['output']!r}")
        print("\n--- End of History ---")


class Runnable(ABC):
    """The central abstraction in agentpipe. Represents any executable operation."""

    @abstractmethod
    def _invoke(self, context: PipeContext) -> PipeContext:
        """
        Core execution logic. Takes a context, performs an action, and returns
        an updated context. This method should not be called directly by users.
        """
        ...

    def __call__(self, initial_input: Any = None, **kwargs) -> 'PipeResult':
        """
        Public execution method. Makes the Runnable callable like a function.
        Returns a PipeResult object containing the final output and history.
        """
        logger.info(f"Starting pipe execution with: {self!r}")
        if initial_input is None and kwargs:
            initial_input = kwargs
        
        context = PipeContext(initial_input)
        initial_pipe_value = context.pipe_value
        final_context = self._invoke(context)
        
        # If no steps were logged by a Pipe, log this execution as a single step.
        if not final_context.history:
            final_context.history.append({
                "name": repr(self),
                "input": initial_pipe_value,
                "output": final_context.pipe_value,
            })
            
        logger.info("Pipe execution finished.")
        return PipeResult(
            final_output=final_context.pipe_value,
            state=final_context.state,
            history=final_context.history
        )

    def __or__(self, other: Union['Runnable', Callable]) -> 'Pipe':
        """
        Implements the | operator to chain Runnables together.
        Automatically wraps callables (like lambdas) into a `Lambda` runnable.
        """
        runnable_other = other
        if not isinstance(runnable_other, Runnable):
            if callable(runnable_other):
                runnable_other = Lambda(runnable_other)
            else:
                raise TypeError(
                    f"Cannot pipe with object of type {type(other)}. "
                    "Must be a Runnable or callable."
                )

        if isinstance(self, Pipe):
            self.runnables.append(runnable_other)
            return self
        return Pipe(self, runnable_other)

    def as_(self, name: str) -> 'Runnable':
        """
        Saves the output of this Runnable into the workflow state under `name`.
        """
        return Saver(self, name)


class Lambda(Runnable):
    """A Runnable that wraps a Python callable (like a lambda function)."""
    def __init__(self, func: Callable):
        super().__init__()
        self.func = func

    def __repr__(self):
        try:
            return f"lambda:{self.func.__name__}"
        except AttributeError:
            return "lambda"

    def _invoke(self, context: PipeContext) -> PipeContext:
        context.pipe_value = self.func(context.pipe_value)
        return context


class Loop(Runnable):
    """A Runnable that executes a body as long as a condition is met."""

    def __repr__(self):
        return (
            f"loop(condition={self.condition!r}, body={self.body!r}, "
            f"max_iterations={self.max_iterations})"
        )

    def __init__(self, condition: 'Runnable', body: 'Runnable', max_iterations: int = 10):
        super().__init__()
        self.condition = condition
        self.body = body
        self.max_iterations = max_iterations

    def _invoke(self, context: PipeContext) -> PipeContext:
        current_context = context
        for i in range(self.max_iterations):
            logger.debug(f"Loop iteration {i+1}/{self.max_iterations}")

            # --- Condition Check ---
            # We invoke on a copy to prevent the condition from altering the main context
            condition_context_after = self.condition._invoke(current_context.copy())
            condition_result = condition_context_after.pipe_value

            # If the condition was a complex pipe, it has its own history. Merge it.
            current_context.history.extend(condition_context_after.history)

            if not condition_result:
                logger.debug("Loop condition is false. Exiting loop.")
                return current_context

            # --- Body Execution ---
            # The body is invoked on the main context, mutating it for the next iteration.
            # Its internal steps will be added to the history by its own _invoke method if it's a Pipe.
            logger.debug(f"Executing loop body: {self.body!r}")
            current_context = self.body._invoke(current_context)

        logger.warning(f"Loop reached max iterations ({self.max_iterations}). Exiting.")
        return current_context


class Pipe(Runnable):
    """A Runnable that represents a sequential chain of other Runnables."""

    def __repr__(self) -> str:
        return " | ".join(repr(r) for r in self.runnables)

    def __init__(self, *runnables: Runnable):
        super().__init__()
        self.runnables: List[Runnable] = list(runnables)

    def _invoke(self, context: PipeContext) -> PipeContext:
        current_context = context
        for runnable in self.runnables:
            logger.debug(f"Executing step in Pipe: {runnable!r}")
            input_value = current_context.pipe_value
            # Execute the step
            current_context = runnable._invoke(current_context)
            output_value = current_context.pipe_value
            
            # Record the step in the history
            step_info = {
                "name": repr(runnable),
                "input": input_value,
                "output": output_value,
            }
            if isinstance(runnable, Saver):
                step_info["saved_as"] = runnable.name
            current_context.history.append(step_info)
            
        return current_context

    def __or__(self, other: 'Runnable') -> 'Pipe':
        """Flattens nested pipes when chaining."""
        return Pipe(*self.runnables, other)


class Saver(Runnable):
    """A wrapper Runnable that saves the result of another Runnable to state."""

    def __repr__(self):
        return f"{self.runnable!r}.as_('{self.name}')"

    def __init__(self, runnable: Runnable, name: str):
        super().__init__()
        self.runnable = runnable
        self.name = name

    def _invoke(self, context: PipeContext) -> PipeContext:
        # Run the wrapped runnable first
        context = self.runnable._invoke(context)
        # Save its pipe_value to the state
        logger.debug(f"Saving output to state key '{self.name}'.")
        context.state[self.name] = context.pipe_value
        return context
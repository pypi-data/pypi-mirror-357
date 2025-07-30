import logging
import zenllm
import jinja2
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict, List, Optional, Union
from .runnable import Lambda, Loop, Runnable
from .context import PipeContext
from .tools import Tool

logger = logging.getLogger(__name__)


class Instruct(Runnable):
    """A Runnable that calls an LLM with a formatted prompt."""

    def __repr__(self) -> str:
        # Truncate long prompts for readability in history logs
        template = self.prompt_template.replace('\n', ' ')
        prompt_repr = (template[:70] + '...') if len(template) > 70 else template
        return f"instruct('{prompt_repr}')"

    def __init__(self, prompt_template: str, tools: Optional[List[Tool]] = None):
        super().__init__()
        self.prompt_template = prompt_template
        self.tools = tools

    def _invoke(self, context: PipeContext) -> PipeContext:
        format_context = context.get_format_context()

        try:
            template = jinja2.Template(
                self.prompt_template,
                variable_start_string="{{",
                variable_end_string="}}",
                autoescape=False,
            )
            prompt = template.render(format_context)
        except Exception as e:
            logger.error(f"Error rendering Jinja2 template for prompt '{self.prompt_template[:100]}...': {e}")
            raise e

        logger.debug(f"Formatted prompt sent to LLM: {prompt}")
        
        # zenllm is a fictional library for this example.
        # We assume it has an API compatible with this usage.
        if self.tools:
            # The spec implies a tool-calling loop is handled by the LLM call.
            tool_schemas = [t.to_json() for t in self.tools]
            response = zenllm.prompt(prompt, tools=tool_schemas)
        else:
            response = zenllm.prompt(prompt)

        logger.info("Received response from LLM.")
        context.pipe_value = response
        return context


def instruct(prompt_template: str, tools: Optional[List[Tool]] = None) -> Instruct:
    """Factory function to create an Instruct Runnable."""
    return Instruct(prompt_template, tools=tools)


def loop(condition: Runnable, body: Runnable, max_iterations: int = 10) -> Loop:
    """
    Factory function to create a Loop Runnable.

    Executes the `body` runnable repeatedly as long as the `condition`
    runnable returns `True`. The loop stops when `condition` returns `False`
    or `max_iterations` is reached.

    Args:
        condition: A `Runnable` that is executed at the start of each
            iteration. Its final output is evaluated as a boolean. The
            loop continues if `True`.
        body: The `Runnable` to execute in each iteration.
        max_iterations: The maximum number of times to run the loop.

    Example:
        # agent that tries to fix code until tests pass
        fix_loop = loop(
            condition=is_test_failure(),
            body=code_fixer_pipe
        )
    """
    return Loop(condition, body, max_iterations=max_iterations)


class Parallel(Runnable):
    """A Runnable that executes multiple Runnables in parallel."""

    def __repr__(self) -> str:
        keys = list(self.runnables.keys())
        return f"parallel({', '.join(keys)})"

    def __init__(self, **runnables: Runnable):
        super().__init__()
        self.runnables = runnables

    def _invoke(self, context: PipeContext) -> PipeContext:
        results = {}
        keys = list(self.runnables.keys())
        logger.info(f"Starting parallel execution for keys: {keys}")
        with ThreadPoolExecutor() as executor:
            future_to_key = {
                executor.submit(runnable._invoke, context.copy()): key
                for key, runnable in self.runnables.items()
            }
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                result_context = future.result()
                results[key] = result_context.pipe_value
                logger.debug(f"Received result for parallel task '{key}'.")
        
        logger.info("Parallel execution finished.")
        context.pipe_value = results
        # Also merge individual results into the state for later access
        context.state.update(results)
        return context


def parallel(**kwargs: Runnable) -> Parallel:
    """
    Factory function to create a Parallel Runnable.

    Example:
        analysis = parallel(
            sentiment=instruct("What is the sentiment of {input}?"),
            topic=instruct("What is the main topic of {input}?")
        )
        result = analysis("LLMs are powerful.")
        # result is {'sentiment': 'Positive', 'topic': 'AI'}
    """
    return Parallel(**kwargs)


class Route(Runnable):
    """A Runnable that dynamically chooses which path to take."""

    def __repr__(self) -> str:
        paths_repr = list(self.paths.keys())
        return f"route(classifier={self.classifier!r}, paths={paths_repr})"

    def __init__(self, classifier: Runnable, paths: Dict[str, Runnable]):
        super().__init__()
        self.classifier = classifier
        self.paths = paths

    def _invoke(self, context: PipeContext) -> PipeContext:
        # Run the classifier to determine the path
        classifier_context = self.classifier._invoke(context)
        path_key = str(classifier_context.pipe_value).strip()
        logger.info(f"Classifier chose path: '{path_key}'")
        
        if path_key in self.paths:
            path_runnable = self.paths[path_key]
            # The context passed to the selected path includes any state changes
            # made by the classifier.
            return path_runnable._invoke(classifier_context)
        else:
            path_keys = list(self.paths.keys())
            logger.error(f"Path '{path_key}' not found in router paths: {path_keys}")
            raise ValueError(
                f"Path '{path_key}' not found in router paths: {path_keys}"
            )


def route(classifier: Union[Runnable, Callable], paths: Dict[str, Runnable]) -> Route:
    """Factory function to create a Route Runnable."""
    if not isinstance(classifier, Runnable):
        if callable(classifier):
            classifier = Lambda(classifier)
        else:
            raise TypeError(
                f"Classifier must be a Runnable or a callable, not {type(classifier)}"
            )
    return Route(classifier, paths)
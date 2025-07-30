import inspect
import os
import sys
import asyncio
import traceback
from typing import TypeVar, Callable, Any, overload
import atexit
import functools
from loguru import logger

from adaptive_harmony.runtime.context import RecipeContext
from adaptive_harmony.runtime.input import InputConfig

IN = TypeVar("IN", bound=InputConfig)


@overload
def recipe_main(func: Callable[[IN, RecipeContext], Any]): ...


@overload
def recipe_main(func: Callable[[RecipeContext], Any]): ...


# inspired from https://github.com/vovavili/main_function/blob/master/main_function.py
def recipe_main(func):

    if func.__module__ == "__main__":
        logger.debug(f"Starting recipe: {func.__name__}, loading context")
        context = RecipeContext.load()
        logger.trace("Loaded config: {}", context.config)

        # handle parameters
        try:
            args = _get_params(func, context)
        except Exception as e:
            stack_trace = traceback.format_exc()
            logger.exception(f"Error preparing arguments for {func.__name__}", exception=e)
            context.job.report_error(stack_trace)
            sys.exit(1)

        def run_recipe():
            func_with_args = functools.partial(func, *args)
            try:
                logger.debug(f"Running recipe function: {func.__name__}")
                if inspect.iscoroutinefunction(func):
                    asyncio.run(func_with_args())
                else:
                    func_with_args()
                logger.info(f"Recipe {func.__name__} completed successfully.")
            except Exception as e:
                stack_trace = traceback.format_exc()
                context.job.report_error(stack_trace)
                logger.exception(f"Exception in recipe function {func.__name__}", exception=e)
                os._exit(1)

        def _atexit_clean_excepthook(etype: Any, value: Any, tb: Any) -> None:
            """Defers the execution of the main function until clean, no-error termination
            of the program."""
            try:
                atexit.unregister(run_recipe)
            except Exception:
                # run_recipe may not be registered; ignore if so
                pass
            sys.__excepthook__(etype, value, tb)

        sys.excepthook = _atexit_clean_excepthook
        atexit.register(run_recipe)

    return func


def _get_params(func, context: RecipeContext) -> list[Any]:
    args: list[Any] = []
    sig = inspect.signature(func)
    assert len(sig.parameters.items()) <= 2, "Support only functions with 2 parameters or less"

    for _, param in sig.parameters.items():
        # Ensure param.annotation is a type before using issubclass
        if isinstance(param.annotation, type):
            if issubclass(param.annotation, RecipeContext):
                args.append(context)
            elif issubclass(param.annotation, InputConfig):
                if context.config.user_input_file:
                    user_input = param.annotation.load_from_file(context.config.user_input_file)
                else:
                    user_input = param.annotation()
                logger.trace("Loaded user input: {}", user_input)
                args.append(user_input)
        else:
            raise TypeError(f"Parameter '{param.name}' must have a type annotation.")

    return args

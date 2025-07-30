"""
Python decorators that can be used by connectors
"""

import functools
import logging
import tracemalloc
from typing import Type, Any

from r7_surcom_api import constants
from r7_surcom_api.more_data import MoreDataManager


# Report the top N memory allocations
MALLOC_REPORT_N = 5

# Report memory allocations above (bytes)
MALLOC_REPORT_THRESHOLD = 1000 * 1000

# TODO: add test for this module


def _move_settings_to_kwargs(
    kwargs: dict,
    settings_class=None
):
    """
    We assume that all other arguments other than constants.FUNCTION_KEYWORD_PARAMS are
    Connector Settings

    Add a `settings` property to kwargs which is a dict of everything
    except whats in constants.FUNCTION_KEYWORD_PARAMS

    If we add the key to `settings`, remove it from kwargs

    If `settings` is already in kwargs, if there is a settings_class
    then we assume it is a dict and we convert it to the class and return,
    else we do noting

    Since kwargs is a dict passed by reference, there is no need
    to return it

    :param kwargs: the kwargs we pass to the fn
    :type kwargs: dict
    """
    settings = {}

    # If settings is already in kwargs, if there is a settings_class
    # then we assume it is a dict and we convert it to the class and we just return
    if constants.SETTINGS_PARAM in kwargs:
        if settings_class:
            kwargs[constants.SETTINGS_PARAM] = settings_class(kwargs[constants.SETTINGS_PARAM])
        return

    for s_key in list(kwargs.keys()):

        if s_key in constants.FUNCTION_KEYWORD_PARAMS:
            continue

        settings[s_key] = kwargs.pop(s_key, None)

    # If we have a settings_class, convert the dict to the class
    if settings_class:
        settings = settings_class(settings)

    kwargs[constants.SETTINGS_PARAM] = settings


def paged_function(
        key: str = None,
        manager_class=MoreDataManager,
        log_more_data: bool = False,
        include_settings: bool = False,
        settings_class: Type[Any] = None,
):
    """Wrap import functions, to simplify handling of the more_data and more_flag.

    Methods wrapped with this function receive a parameter 'more_data' which is a MoreDataManager.
    They can use this to set and get values from the pagination store, without dealing with any
    of the implementation details.

    The function should return a dictionary with keys/values that it wants to put into the workflow
    (typically {"items": [...]} but additional keys are fine).  The wrapper adds a 'more_data' dict
    and a 'more_flag' boolean into the workflow that capture the MoreDataManager status.

    @param key: Optional, key for data storage.  By default the key is the function name.
    """

    def decorator(func):

        # Note: we're changing the signature type of more_data, don't copy __annotations__
        @functools.wraps(func, assigned=("__module__", "__name__", "__qualname__", "__doc__"))
        def wrap(__user_log: logging.Logger, *args, **kwargs):

            snap1 = None
            snap2 = None
            mem1 = 0
            peak1 = 0
            if tracemalloc.is_tracing():
                snap1 = tracemalloc.take_snapshot()
                tracemalloc.reset_peak()
                mem1, peak1 = tracemalloc.get_traced_memory()

            # Build a data key for the function.  The function's storage will be under this key.
            func_data_key = f"{func.__module__}:{func.__name__}"
            if key:
                __user_log.debug("Wrapping function %s with key %s", func_data_key, key)
                func_data_key = key
            else:
                __user_log.debug("Wrapping function %s", func_data_key)

            # get the more_data from the function input param
            # then copy it, so we can update it and pass in a fake one
            more_data_input = kwargs.get("more_data") or {}

            # Make a MoreDataManager for the function to use
            mdm = manager_class(__user_log, more_data_input, func_data_key)

            # Set the kwargs "more_data" to the MoreDataManager instance
            # (the original function has no need to access the actual more_data dict)
            kwargs["more_data"] = mdm

            if include_settings:
                # Populate kwargs with the connector settings
                _move_settings_to_kwargs(kwargs, settings_class)

            # call the wrapped function
            func_result = func(__user_log, *args, **kwargs) or {}

            if tracemalloc.is_tracing():
                snap2 = tracemalloc.take_snapshot()
                mem2, peak2 = tracemalloc.get_traced_memory()
                if mem2 - mem1 > MALLOC_REPORT_THRESHOLD:
                    __user_log.info("%s bytes allocated extra", mem2 - mem1)
                if peak2 - peak1 > MALLOC_REPORT_THRESHOLD:
                    __user_log.info("%s bytes allocated extra peak", peak2 - peak1)
                diffs = snap2.compare_to(snap1, "lineno", cumulative=True)
                for diff in diffs[:MALLOC_REPORT_N]:
                    if diff.size_diff < MALLOC_REPORT_THRESHOLD:
                        break
                    __user_log.info("%s bytes allocated in %s", diff.size_diff, diff.traceback)

            # Update the func_result with more_data and more_flag, then return it to the workflow
            return mdm.get_result(func_result, log_more_data=log_more_data)

        return wrap

    return decorator


# Replacement for `paged_function` for connectors developed with the surcom-sdk
# We set `include_settings` to `True` so only surcom_functions will have `settings` in their kwargs
def surcom_function(settings_class=None, **kwargs):

    return paged_function(
        include_settings=True,
        settings_class=settings_class,
        **kwargs
    )


def surcom_test_function(settings_class=None):

    def surcom_test_function_decorator(fn, *args, **kwargs):
        """
        The decorated function

        :param fn: The function to decorate
        """

        @functools.wraps(fn)
        def _invoke_surcom_test_function(__user_log: logging.Logger, *args, **kwargs):
            """
            The code to call when a function with the decorator `@surcom_test_function()` is invoked
            """
            kwargs["__user_log"] = __user_log

            # Populate kwargs with the connector settings
            _move_settings_to_kwargs(kwargs, settings_class)

            return fn(*args, **kwargs)

        return _invoke_surcom_test_function

    return surcom_test_function_decorator

"""
Looping helpers for 'more_data' / 'more_flag' pagination for import feeds

For a single import-feed function, this simplifies dealing with pagination
and other context from the source.  It allows you to easily track multi-step
data sources with common patterns such as these:
- a page identifier ("offset", "cursor", "NextToken" etc.) that tells the
  next page where to fetch; along with any other temporary data that you want
  to store between pages.
- a list of items that should be processed singly or in batches.
- a state machine where the state transitions between (e.g.): "start", "report requested",
  "report ready", "report downloaded", and the function has different processing
  depending on the state.

For imports that work with multiple dependent types, for example machines that
each reference IP addresses (by producing the full IP object) or other entities
such as policies or users (by producing a reference to the object, which should
be fetched from the source), this simplifies the following reliable pattern:
- the "get machines" function produces a list of machines, as 'items',
  that can be loaded into the graph by following the function with 'enqueue';
- the "get machines" function also produces lists of dependent entities, and
  returns them as additional properties (not named 'items', the name doesn't matter).
- a subsequent "get policies" function whose input maps from the list of policy
  entities, or policy IDs, produced by the "get machines" function; it aggregates
  and deduplicates this list, and fetches batches of the relevant data, producing
  'items' that can be loaded into the graph;
- this pattern can be repeated for multiple dependent objects, or even
  for chains of dependent-of-dependent objects as needed.

The classes are:
- MoreDataManager, the base class, manages a single item such as an offset or cursor (plus any "extra" data)
- MoreDataListManager, manages a list of items
- MoreDataDictManager, manages a dictionary of values (with keys that we can dedup)

"""

from typing import Generator, Tuple, Union
import json
import time

from r7_surcom_api.types import SurcomType

# Special value meaning "we're finished"
NO_MORE_DATA = -1

# Special extra-data keys for the list and dict managers' internal use
EXTRA_DONE_KEY = "_done_"
EXTRA_FAIL_KEY = "_fail_"

# If a timeout is not specified, we won't iterate more than this (seconds)
MAX_ITERATION_TIME = 200

# Global Extras Key
GLOBAL_EXTRAS_KEY = "_global_extras_"

RUNNING_TOTAL_KEY = "_running_total_"


def get_more_flag(more_data: dict):
    """
    Calculate the 'more' flag for paging data sources
    Returns True if any values in 'more_data' are not NO_MORE_DATA
    Variables related to keeping the count of the entities are prefixed with _
    """
    return any(
        value != NO_MORE_DATA
        for key, value in more_data.items()
        if not key.startswith("_")
    )


class _jsondict(dict):
    """
    A dict with string keys and JSON-safe values
    """
    def __setitem__(self, __key, __value) -> None:
        if not isinstance(__key, str):
            raise TypeError(f"Key '{__key}' must be a string.")
        # Throw a TypeError if the value is not JSON-serializable
        json.dumps(__value)
        return super().__setitem__(__key, __value)


class MoreDataManager:
    """
    Base class to manage more_data for a single value.  Also allows storing arbitrary "extra data" in a dictionary.

    Typical usage:

    @paged_function()
    def myfunc(__user_log, more_data: MoreDataManager, other_stuff):

        # If we've already paged through all the data, there's nothing to do
        if more_data.is_done():
            return {"items": []}

        # Get the saved cursor value, call the API, and update the saved cursor value.
        cursor = more_data.get(default=0)
        items, updated_cursor = call_the_external_api(other_stuff, cursor)
        more_data.set(updated_cursor)
        return {
            "items": items
        }

    """
    def __init__(self, __user_log, more_data: dict, key: str):
        """
        Construct from a dictionary of 'more_data' values
        """
        if not key or not isinstance(key, str):
            raise TypeError("The more_data key must be a string.")
        self._log = __user_log
        self._key = key
        self._extra_key = f"_{key}"
        if isinstance(more_data, _jsondict):
            self._more_data = more_data
        elif isinstance(more_data, dict):
            self._more_data = _jsondict(more_data)
        elif more_data is None:
            self._more_data = _jsondict()
        else:
            raise ValueError(f"Invalid more_data: {more_data}")

    def __repr__(self) -> str:
        # repr for printf-debugging
        return f"{self.__class__.__name__}('{self._key}')=" + json.dumps(self._more_data.get(self._key))

    # Alternate constructor

    @classmethod
    def new(cls, inst: 'MoreDataManager', name: str = None):
        """
        If you already have a MoreDataManager, you can make another that uses a different name on the same more_data.
        (This is cheap, you can just construct these dependent managers as and when you need to use them)
        """
        # The more_data key might be a string "module:function", in which case retain the part before the colon.
        prefix, _, _ = inst._key.partition(":")
        return cls(inst._log, inst._more_data, f"{prefix}:{name}")

    # Simple getter and setter (for managing a state value)

    def get(self, default=None):
        """
        Get the saved value
        """
        return self._get(default=default)

    def _get(self, default=None):
        # get the value from more_data
        return self._more_data.get(self._key, default)

    def set(self, value):
        """
        Set a value
        """
        self._set(value)

    def _set(self, value):
        # Just store the value in more_data under the key.
        self._more_data[self._key] = value

    def done(self):
        """
        Mark that we're done
        """
        # Note: even when done, we keep any extras in case they're wanted later
        self._set(NO_MORE_DATA)

    def is_done(self) -> bool:
        """
        Did we finish all the processing?
        """
        return self._get() == NO_MORE_DATA

    # 'extra' is just a dictionary for storing random stuff

    @property
    def extra(self) -> dict:
        """
        A dictionary for storing any extra data associated with the function
        """
        if not self._more_data.get(self._extra_key):
            self._more_data[self._extra_key] = _jsondict()
        return self._more_data[self._extra_key]

    @property
    def global_extras(self) -> dict:
        """
        A dictionary for storing any global extra data that is shared
        across Functions
        """
        if not self._more_data.get(GLOBAL_EXTRAS_KEY):
            self._more_data[GLOBAL_EXTRAS_KEY] = _jsondict()
        return self._more_data[GLOBAL_EXTRAS_KEY]

    # Helper to merge the function's raw result
    # (typically called by the decorator wrapper, not by the connector function itself)
    def get_result(
        self,
        func_result: Union[dict, list],
        log_more_data: bool = False
    ) -> dict:
        """
        Given a func_result (which is a dict or list), we add the more_data and more_flag
        to the result.  This is typically called by the decorator wrapper, not by the connector function itself.

        :param func_result: The result of the function, which is a dict or list.
        :type func_result: Union[dict, list]
        :param log_more_data: if True, log out the contents of more_data, defaults to False
        :type log_more_data: bool, optional
        :return: The result of the function, which is a dict with more_data and more_flag added.
        :rtype: dict
        """
        if func_result is None:
            func_result = {}

        # If the function just returns a list, we assume its a list of SurcomTypes
        # so we convert it into a dict of `items` as the platform expects it
        if isinstance(func_result, list):
            items = []
            for i in func_result:

                if isinstance(i, SurcomType):
                    items.append(
                        i.to_batch_item()
                    )
                else:
                    items.append(i)

            func_result = {"items": items}

            running_total = self.extra.get(RUNNING_TOTAL_KEY, 0)
            current_total = len(items)
            new_running_total = running_total + current_total
            self.extra[RUNNING_TOTAL_KEY] = new_running_total

            items_str = "item"

            if current_total != 1:
                items_str = "items"

            self._log.info(f"Found '{current_total}' {items_str} in this page. Gathered "
                           f"'{new_running_total}' {items_str} in total so far.")

        if not isinstance(func_result, dict):
            raise TypeError(f"Expected function to return a dict, not {type(func_result)}")

        if log_more_data:
            self._log.info("more_data: %s", json.dumps(json.dumps(self._more_data)))
        else:
            self._log.debug("more_data: %s", self._more_data)

        func_result.update({
            "more_data": self._more_data,
            "more_flag": get_more_flag(self._more_data)
        })
        return func_result


class MoreDataListManager(MoreDataManager):
    """
    Class to manage more_data for a list of values.

    Typical usage:

    @paged_function(manager_class=MoreDataListManager)
    def myfunc(__user_log, more_data: MoreDataListManager, list_of_new_ids_to_fetch: list):

        # If we were given a list of things to do, e.g. IDs to fetch, update them into the MoreDataManager.
        more_data.update(list_of_new_ids_to_fetch)

        # Now we can iterate some (or all) of the things to be done, and process them.
        items = []
        for id in more_data.todo(limit=10):

            items.append(some_external_api.get(id))

            # We completed that one, mark it done (*required*)
            more_data.done(id)

        return {
            "items": items
        }

    """
    def set(self, _):
        """
        Setting a value directly is not supported here
        """
        raise NotImplementedError("Don't use set(), use update()")

    def update(self, ids: list):
        """
        Update a list of values with 'ids' (which may be a string, or a list of strings)
        Note: you MUST call update() at least once.  If your update is empty, call update() with an empty list.
        """
        # Make a list
        if isinstance(ids, dict):
            raise TypeError("MoreDataListManager requires a list of ids, not a dictionary")
        if not ids:
            ids = []
        if not isinstance(ids, list):
            ids = [ids]

        # The list we had previously stored
        data = self.get()
        if data == NO_MORE_DATA:
            data = None
        if data is None:
            data = []

        # Build the combined list of things previously to do, and new to do
        data = list(set(data + ids))
        self._set(data)

        # Consolidate (remove any already done, and recalculate the overall lists)
        self._consolidate()

    def _consolidate(self):
        # The list of items todo, done, failed/notfound
        data = self.all_todo()
        done = sorted(list(set(self.extra.get(EXTRA_DONE_KEY, []))), key=str)
        failed = sorted(list(set(self.extra.get(EXTRA_FAIL_KEY, []))), key=str)

        # Update the todo list, removing done and failed/notfound
        todo = sorted(list(set(data) - set(done) - set(failed)), key=str)

        # Update the more_data
        if todo:
            self._set(todo)
            self.extra[EXTRA_DONE_KEY] = done
            self.extra[EXTRA_FAIL_KEY] = failed
        else:
            # Note: even when done, we keep the lists of "done/failed" and any "extra" in case they're wanted later
            self._set(NO_MORE_DATA)

    def all_todo(self) -> list:
        """
        Get the list of all values that remain to be done.
        Note: the caller should not update this directly.  Instead use update().
        """
        data = self.get()

        # Maybe we thought we were done already, in which case treat as an empty list
        if data is None or data == NO_MORE_DATA:
            return []

        # If the more_data value was not a list, the caller messed up somehow
        if not isinstance(data, list):
            raise TypeError(f"Expected a list, not {type(data)}: '{data}'")

        return data

    def todo(self, limit: int = None, time_limit_seconds: int = MAX_ITERATION_TIME) -> Generator[str, None, None]:
        """
        Iterate (up to 'limit', or up to 'time_limit_seconds') values that remain to be done
        """
        time0 = time.perf_counter()
        for id in self.all_todo()[:limit]:
            if time_limit_seconds:
                if time.perf_counter() - time0 > time_limit_seconds:
                    return
            yield id

    def all_done(self):
        """
        Mark all as done
        """
        todo = list(self.all_todo())
        done = sorted(list(set(self.extra.get(EXTRA_DONE_KEY, []) + todo)), key=str)
        self.extra[EXTRA_DONE_KEY] = done
        self._consolidate()

    def done(self, id: str):
        """
        Mark 'id' as done successfully
        """
        done = sorted(list(set(self.extra.get(EXTRA_DONE_KEY, []) + [id])), key=str)
        self.extra[EXTRA_DONE_KEY] = done
        self._consolidate()

    def fail(self, id: str):
        """
        Mark 'id' as failed or not found (will not be retried)
        """
        failed = sorted(list(set(self.extra.get(EXTRA_FAIL_KEY, []) + [id])), key=str)
        self.extra[EXTRA_FAIL_KEY] = failed
        self._consolidate()

    def stats(self) -> str:
        """
        A string describing the number of things
        """
        todo = len(self.all_todo())
        done = len(self.extra.get(EXTRA_DONE_KEY, []))
        failed = len(self.extra.get(EXTRA_FAIL_KEY, []))
        return f"done {done}, not found {failed}, to do {todo}"


class MoreDataDictManager(MoreDataManager):
    """
    Class to manage more_data for a keyed dictionary of values.

    Typical usage:

    @paged_function(manager_class=MoreDataDictManager)
    def myfunc(__user_log, more_data: MoreDataDictManager, new_data_to_track: dict):

        # If we were given a dict of things to do, update them into the MoreDataManager.
        more_data.update(new_data_to_track)

        # Now we can iterate some (or all) of the things to be done, and process them.
        items = []
        for key, value in more_data.todo(limit=10):

            items.append(some_external_api.get(key, value))

            # We completed that one, mark it done (or .fail(key) to mark it failed or not found)
            more_data.done(key)

        return {
            "items": items
        }

    """

    def get(self, id: str, default=None):
        """
        Get from the dictionary, i.e.
        - get the value under the id if this id is in the list of "todo" items
        - return default (None) otherwise
        """
        return self.all_todo().get(id, default)

    def set(self, _):
        """
        Setting a value directly is not supported here
        """
        raise NotImplementedError("Don't use set(), use update()")

    def update(self, values: dict, force_update: bool = False):
        """
        Update a collection of values with 'values' (a dictionary with unique keys).
        Note: you MUST call update() at least once.  If your update is empty, call update() with an empty dict.
        """
        # Make a dict
        if not isinstance(values, dict):
            raise TypeError("MoreDataDictManager requires a dictionary")

        # The values we had previously stored
        data = self._more_data.get(self._key)
        if data == NO_MORE_DATA:
            data = None
        if data is None:
            data = _jsondict()
            self._set(data)

        # Update the store by adding anything new from the 'values' dict.
        # Note: by default, if a key was already there, do not update its value.
        #       However, if `force_update` is set to `True` we do overwrite it
        for key, value in values.items():

            if force_update:
                data[key] = value

            else:
                if key not in data:
                    data[key] = value

        # Consolidate (remove any already done, and recalculate the overall lists)
        self._consolidate()

    def _consolidate(self):
        # The list of items todo, done, failed/notfound
        data = self.all_todo()
        done = sorted(list(set(self.extra.get(EXTRA_DONE_KEY, []))), key=str)
        failed = sorted(list(set(self.extra.get(EXTRA_FAIL_KEY, []))), key=str)

        # Update the todo list, removing done and failed/notfound
        for key in set(done):
            data.pop(key, None)
        for key in set(failed):
            data.pop(key, None)

        # Update the more_data
        if data:
            self._set(data)
            self.extra[EXTRA_DONE_KEY] = done
            self.extra[EXTRA_FAIL_KEY] = failed
        else:
            # Note: even when done, we keep the lists of "done/failed" and any "extra" in case they're wanted later
            self._set(NO_MORE_DATA)

    def all_todo(self) -> dict:
        """
        Get the dictionary of all keys that remain to be done.
        Note: the caller should not update this directly.  Instead use update().
        """
        data = self._more_data.get(self._key)

        # Maybe we thought we were done already, in which case treat as an empty dict
        if data is None or data == NO_MORE_DATA:
            return {}

        # If the more_data value was not a dict, the caller messed up somehow
        if not isinstance(data, dict):
            raise TypeError(f"Expected a dict, not {type(data)}: '{data}'")

        return data

    def todo(self, limit: int = None, time_limit_seconds: int = MAX_ITERATION_TIME) -> \
            Generator[Tuple[str, dict], None, None]:
        """
        Iterate (up to 'limit', or up to 'time_limit_seconds') keys and values that remain to be done
        """
        time0 = time.perf_counter()
        todo_dict = self.all_todo()
        keys = sorted(list(todo_dict), key=str)[:limit]
        for key in keys:
            if time_limit_seconds:
                if time.perf_counter() - time0 > time_limit_seconds:
                    return
            yield key, todo_dict[key]

    def all_done(self):
        """
        Mark all as done
        """
        todo = list(self.all_todo())
        done = sorted(list(set(self.extra.get(EXTRA_DONE_KEY, []) + todo)), key=str)
        self.extra[EXTRA_DONE_KEY] = done
        self._consolidate()

    def done(self, key: str):
        """
        Mark 'key' as done successfully
        """
        done = sorted(list(set(self.extra.get(EXTRA_DONE_KEY, []) + [key])), key=str)
        self.extra[EXTRA_DONE_KEY] = done
        self._consolidate()

    def fail(self, key: str):
        """
        Mark 'key' as failed
        """
        failed = sorted(list(set(self.extra.get(EXTRA_FAIL_KEY, []) + [key])), key=str)
        self.extra[EXTRA_FAIL_KEY] = failed
        self._consolidate()

    def stats(self) -> str:
        """
        A string describing the number of things
        """
        todo = len(self.all_todo())
        done = len(self.extra.get(EXTRA_DONE_KEY, []))
        failed = len(self.extra.get(EXTRA_FAIL_KEY, []))
        return f"done {done}, not found {failed}, to do {todo}"

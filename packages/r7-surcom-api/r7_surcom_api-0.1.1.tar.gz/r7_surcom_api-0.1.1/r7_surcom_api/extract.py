import abc
import itertools
import os
from typing import Callable, Optional, Generator, Iterable, Union, Iterator, List

from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from r7_surcom_api import SurcomType

_WAIT_MIN = int(os.getenv('EXTRACT_WAIT_MIN', '10'))
_WAIT_MAX = int(os.getenv('EXTRACT_WAIT_MAX', '60'))
_STOP_AFTER = int(os.getenv('EXTRACT_STOP_AFTER', '5'))


class NonRetryableError(Exception):
    """Exception to indicate a non-retryable error."""

    def __init__(self, message: str):
        super().__init__(message)


class ExtractResult:
    """
    Contains a generator of items to be extracted. Recommended to be yielded in batches/chunks.
    """
    _items: Iterator[Union[dict, SurcomType]]

    def __init__(
        self,
        items: Union[
            Generator[Union[dict, SurcomType], None, None],
            Iterable[Union[dict, SurcomType]],
            Iterator[Union[dict, SurcomType]]
        ],
    ):
        if isinstance(items, Iterable):
            # Convert to Iterator if not already
            self._items = iter(items)
        else:
            self._items = items

    def __iter__(self) -> Iterator[Union[dict, SurcomType]]:
        return self._items


class ExtractGenerator:
    """
    Generates ExtractResult objects, which contain a generator of items to be extracted. The preferred return value of
    extract function implementations.
    """

    def __iter__(self):
        return self

    @abc.abstractmethod
    def __next__(self) -> ExtractResult:
        """
        Return a single extract result, which should be a batch/chunk of items to be extracted.
        """
        raise NotImplementedError()

    def set_resumable_state(
        self,
        last_state: dict,
    ):
        """
        Set the resumable state of the generator.
        """
        pass

    @property
    def resumable_state(self) -> Optional[dict]:
        """
        Return the resumable state of the generator. The value of which may be stored after processing the last
        ExtractResult returned by the generator, so it may be resumable later.
        """
        return None


@retry(
    wait=wait_exponential(multiplier=2, min=_WAIT_MIN, max=_WAIT_MAX),
    stop=stop_after_attempt(_STOP_AFTER),
    retry=retry_if_not_exception_type(NonRetryableError)  # Retry on all exceptions except NonRetryableError
)
def call_function_with_retry(
    func: Callable,
    kwargs: dict,
):
    """Call a function with retry logic."""
    return func(**kwargs)


class QueryContext:
    """
    Used to get query results for query inputs. Can be used as an iterator to yield results one by one.
    """

    def __iter__(self):
        return self

    @abc.abstractmethod
    def __next__(self) -> dict:
        """
        Return a single query result
        """
        raise NotImplementedError()

    def set_resumable_state(
        self,
        last_state: dict,
    ):
        """
        Set the resumable state of the query context.
        :param last_state: the last state
        """
        pass

    @property
    def resumable_state(self) -> Optional[dict]:
        """
        Return the resumable state of the query context. The value of which may be stored after processing the last
        ExtractResult returned by the generator, so it may be resumable later.
        :return: the resumable state
        """
        return None

    def batched(
        self,
        batch_size: int = 500,
    ) -> Generator[List[dict], None, None]:
        """
        Get a batching generator over the results for a query.
        :param batch_size: the size of each batch to yield
        :return: a generator which yields each page of results
        """
        batched = itertools.batched(
            self,
            batch_size
        )
        for batch in batched:
            yield list(batch)

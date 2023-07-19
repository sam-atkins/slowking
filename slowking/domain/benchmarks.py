"""
Benchmarking types
"""
import abc
import logging.config
from enum import Enum
from typing import Type

from slowking.domain import commands, events
from slowking.domain.exceptions import MessageNotAssignedToBenchmarkError

logger = logging.getLogger(__name__)


class BenchmarkTypesEnum(Enum):
    """
    All benchmark types must be added to this enum.
    """

    LATENCY = "latency"

    @classmethod
    def get_benchmark_types(cls) -> list[str]:
        return [benchmark_type.value for benchmark_type in list(cls)]


class AbstractBenchmarkType(abc.ABC):
    """
    Abstract base class for benchmark types.
    """

    message_ordering: dict[str, Type[events.Event]]

    @abc.abstractmethod
    def next_event(
        self, current_message: events.Event | commands.Command, benchmark_id: int
    ) -> events.Event | None:
        raise NotImplementedError


class LatencyBenchmark(AbstractBenchmarkType):
    """
    Latency benchmark type.

    Message ordering documents the flow of the benchmark, from external commands to
    internal events.
    """

    message_ordering: dict[str, Type[events.Event]] = {
        commands.CreateBenchmark.__name__: events.BenchmarkCreated,
        events.BenchmarkCreated.__name__: events.ProjectCreated,
        events.ProjectCreated.__name__: events.NoOp,
        commands.UpdateDocument.__name__: events.DocumentUpdated,
        events.DocumentUpdated.__name__: events.AllDocumentsUploaded,
        events.AllDocumentsUploaded.__name__: events.BenchmarkCompleted,
    }

    def next_event(
        self, current_message: events.Event | commands.Command, benchmark_id: int
    ) -> events.Event | None:
        """
        Get the next event in the benchmark flow.

        Args:
            current_message (events.Event | commands.Command): the current event or
            command
            benchmark_id (int): the benchmark id

        Raises:
            MessageNotAssignedToBenchmarkError

        Returns:
            events.Event | None: the next event in the benchmark flow
        """
        result = self.message_ordering.get(type(current_message).__name__)

        if not result:
            raise MessageNotAssignedToBenchmarkError(
                f"{current_message} is not in LatencyBenchmark"
            )
        event = getattr(events, result.__name__)

        if event == events.NoOp:
            logger.info("NoOp message returned")
            return None

        event = event(benchmark_id=benchmark_id)
        return event


def get_next_event(
    benchmark_id: int,
    benchmark_type: str,
    current_message: events.Event | commands.Command,
) -> events.Event | None:
    """
    Get the next event in the benchmark flow.

    Args:
        benchmark_id (int): the benchmark id
        benchmark_type (str): the benchmark type
        current_message (events.Event | commands.Command): the current event or command

    Raises:
        NotImplementedError: raised if an invalid benchmark type is passed

    Returns:
        events.Event | None: the next event in the benchmark flow
    """

    logger.info(f"Getting next message for benchmark_type: {benchmark_type}")
    match benchmark_type:
        case BenchmarkTypesEnum.LATENCY.value:
            bm = LatencyBenchmark()
        case _:
            raise NotImplementedError

    try:
        event = bm.next_event(current_message, benchmark_id)
    except MessageNotAssignedToBenchmarkError as e:
        logger.error(e)
        raise e

    return event

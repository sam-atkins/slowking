import logging
from typing import Callable

from slowking.domain import benchmarks, commands, events
from slowking.domain.model import Benchmark

logger = logging.getLogger(__name__)


def publish_next_event(
    message: events.Event | commands.Command,
    publish: Callable[[events.Event], None],
    benchmark: Benchmark,
) -> None:
    """
    Determines the next event and then publishes it to the eventbus. If there is no next
    event, then it returns None.

    Args:
        message (events.Event | commands.Command): the current message
        publish (Callable[[events.Event], None]): a callable to publish the next event
        benchmark (Benchmark): the benchmark aggregate
    """
    next_event = benchmarks.get_next_event(
        benchmark_id=benchmark.id,
        benchmark_type=benchmark.benchmark_type,
        current_message=message,
    )
    if next_event is None:
        logger.info("=== No next event ===")
        return

    return publish(next_event)

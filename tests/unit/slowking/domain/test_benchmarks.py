import pytest

from slowking.domain import benchmarks, events
from slowking.domain.exceptions import MessageNotAssignedToBenchmarkError


def test_latency_benchmark_next_event():
    benchmark_id = 1
    event = events.BenchmarkCreated(
        benchmark_id=benchmark_id,
    )
    lbm = benchmarks.LatencyBenchmark()
    result = lbm.next_event(current_message=event, benchmark_id=benchmark_id)
    assert result == events.ProjectCreated(benchmark_id=benchmark_id)


def test_latency_benchmark_next_event_is_noop_event():
    """
    In Latency benchmarks, the handler processes the ProjectCreated event by uploading
    documents. The next event is a NoOp event. This is because we wait for the
    instrumented app to send document upload events (start and end upload times).
    """
    benchmark_id = 2
    event = events.ProjectCreated(benchmark_id=benchmark_id)
    lbm = benchmarks.LatencyBenchmark()
    result = lbm.next_event(current_message=event, benchmark_id=benchmark_id)
    assert not result


def test_latency_benchmark_next_event_unassigned_event():
    class FakeEvent(events.Event):
        channel = "fake_event"

    fake_event = FakeEvent(channel="fake_channel", benchmark_id=1)

    lbm = benchmarks.LatencyBenchmark()
    with pytest.raises(MessageNotAssignedToBenchmarkError):
        lbm.next_event(current_message=fake_event, benchmark_id=1)


def test_get_benchmark_types():
    result = benchmarks.BenchmarkTypesEnum.get_benchmark_types()
    assert result == ["latency"]


def test_get_next_event_is_project_created():
    event = events.BenchmarkCreated(
        benchmark_id=1,
    )
    result = benchmarks.get_next_event(
        benchmark_id=1, benchmark_type="latency", current_message=event
    )
    assert result == events.ProjectCreated(benchmark_id=1)


def test_get_next_event_unknown_benchmark_type():
    with pytest.raises(NotImplementedError):
        # ignoring type to test NotImplementedError
        benchmarks.get_next_event(
            benchmark_id=1, benchmark_type="new_benchmark", current_message="fake_event"  # type: ignore # noqa E501
        )


def test_get_next_event_unassigned_event():
    class FakeEvent(events.Event):
        channel = "fake_event"

    fake_event = FakeEvent(channel="fake_channel", benchmark_id=1)

    with pytest.raises(MessageNotAssignedToBenchmarkError):
        benchmarks.get_next_event(
            benchmark_id=1, benchmark_type="latency", current_message=fake_event
        )


def test_get_next_event_noop_event():
    event = events.ProjectCreated(benchmark_id=1)
    result = benchmarks.get_next_event(
        benchmark_id=1, benchmark_type="latency", current_message=event
    )
    assert result is None

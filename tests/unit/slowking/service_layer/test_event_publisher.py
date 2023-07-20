from slowking.domain import events
from slowking.service_layer.event_publisher import publish_next_event


def fake_publish(event):
    return event


def test_publish_next_event(benchmark):
    benchmark.id = 1
    event = events.BenchmarkCreated(
        benchmark_id=1,
    )
    # type ignoring "publish_next_event" does not return a value for testing purposes
    result = publish_next_event(
        message=event, publish=fake_publish, benchmark=benchmark  # type: ignore
    )
    assert result == events.ProjectCreated(benchmark_id=1, channel="project_created")


def test_publish_next_event_returns_none_if_no_next_event(benchmark):
    benchmark.id = 1
    event = events.ProjectCreated(
        benchmark_id=1,
    )

    # type ignoring "publish_next_event" does not return a value for testing purposes
    result = publish_next_event(
        message=event, publish=fake_publish, benchmark=benchmark  # type: ignore
    )
    # assert not result
    assert result is None

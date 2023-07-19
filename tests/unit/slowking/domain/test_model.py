from datetime import datetime, timedelta, timezone

import pytest

from slowking.domain import events, model
from slowking.domain.exceptions import MessageNotAssignedToBenchmarkError


def test_validate_benchmark_type():
    docs = [model.Document(name="doc test", file_path="path/to/file")]
    project = model.Project(
        name="test project",
        document=docs,
        eigen_project_id=20,
    )
    bm = model.Benchmark(
        name="latency benchmark for release 1.0.0",
        benchmark_type="latency",
        eigen_platform_version="v1.0.0",
        target_infra="kubernetes",
        target_url="http://localhost:8080",
        username="test_user",
        password="test_password",
        project=project,
    )
    assert bm.benchmark_type == model.BenchmarkTypesEnum.LATENCY.value


def test_validate_benchmark_type_raises_exception_when_benchmark_type_is_not_valid():
    docs = [model.Document(name="doc test", file_path="path/to/file")]
    project = model.Project(
        name="test project",
        document=docs,
        eigen_project_id=20,
    )
    with pytest.raises(model.InvalidBenchmarkTypeError):
        model.Benchmark(
            name="latency benchmark for release 1.0.0",
            benchmark_type="notAValidBenchmarkType",
            eigen_platform_version="v1.0.0",
            target_infra="kubernetes",
            target_url="http://localhost:8080",
            username="test_user",
            password="test_password",
            project=project,
        )


def test_document_upload_time_returns_none_when_no_end_time():
    doc = model.Document(
        name="doc.txt",
        file_path="/home/app/artifacts/doc.txt",
    )
    doc.upload_time_start = datetime.now(timezone.utc)
    doc.upload_time_end = None  # type: ignore
    assert doc.upload_time is None


def test_document_upload_time_returns_none_if_no_times():
    doc = model.Document(
        name="doc.txt",
        file_path="/home/app/artifacts/doc.txt",
    )
    doc.upload_time_start = None  # type: ignore
    doc.upload_time_end = None  # type: ignore
    assert doc.upload_time is None


def test_document_upload_time_returns_upload_time():
    doc = model.Document(
        name="doc.txt",
        file_path="/home/app/artifacts/doc.txt",
    )
    now = datetime.now(timezone.utc)
    doc.upload_time_start = now - timedelta(seconds=10)
    doc.upload_time_end = now
    assert doc.upload_time is not None
    assert doc.upload_time == 10.0


def test_latency_benchmark_next_event():
    benchmark_id = 1
    event = events.BenchmarkCreated(
        benchmark_id=benchmark_id,
    )
    lbm = model.LatencyBenchmark()
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
    lbm = model.LatencyBenchmark()
    result = lbm.next_event(current_message=event, benchmark_id=benchmark_id)
    assert not result


def test_latency_benchmark_next_event_unassigned_event():
    class FakeEvent(events.Event):
        channel = "fake_event"

    fake_event = FakeEvent(channel="fake_channel", benchmark_id=1)

    lbm = model.LatencyBenchmark()
    with pytest.raises(MessageNotAssignedToBenchmarkError):
        lbm.next_event(current_message=fake_event, benchmark_id=1)


def test_get_benchmark_types():
    result = model.BenchmarkTypesEnum.get_benchmark_types()
    assert result == ["latency"]


def test_get_next_event_is_project_created():
    event = events.BenchmarkCreated(
        benchmark_id=1,
    )
    result = model.get_next_event(
        benchmark_id=1, benchmark_type="latency", current_message=event
    )
    assert result == events.ProjectCreated(benchmark_id=1)


def test_get_next_event_unknown_benchmark_type():
    with pytest.raises(NotImplementedError):
        # ignoring type to test NotImplementedError
        model.get_next_event(
            benchmark_id=1, benchmark_type="new_benchmark", current_message="fake_event"  # type: ignore # noqa E501
        )


def test_get_next_event_unassigned_event():
    class FakeEvent(events.Event):
        channel = "fake_event"

    fake_event = FakeEvent(channel="fake_channel", benchmark_id=1)

    with pytest.raises(MessageNotAssignedToBenchmarkError):
        model.get_next_event(
            benchmark_id=1, benchmark_type="latency", current_message=fake_event
        )


def test_get_next_event_noop_event():
    event = events.ProjectCreated(benchmark_id=1)
    result = model.get_next_event(
        benchmark_id=1, benchmark_type="latency", current_message=event
    )
    assert result is None

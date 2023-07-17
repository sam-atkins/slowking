from datetime import datetime, timedelta, timezone

import pytest
from pydantic import SecretStr

from slowking.domain import commands, events, model
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


# TODO implement test
def test_latency_benchmark_next_message():
    pass


def test_latency_benchmark_next_message_unassigned_event():
    class FakeEvent(events.Event):
        channel = "fake_event"

    fake_event = FakeEvent(channel="fake_channel", benchmark_id=1)

    lbm = model.LatencyBenchmark()
    with pytest.raises(MessageNotAssignedToBenchmarkError):
        lbm.next_message(fake_event)


def test_get_benchmark_types():
    result = model.BenchmarkTypesEnum.get_benchmark_types()
    assert result == ["latency"]


def test_get_next_message_is_project_created():
    secret_pw = SecretStr("test_password")
    event = events.BenchmarkCreated(
        benchmark_id=1,
        name="latency benchmark",
        benchmark_type="latency",
        target_infra="kubernetes",
        target_url="http://localhost:8080",
        target_eigen_platform_version="1.0.0",
        username="test_user",
        password=secret_pw,
    )
    result = model.get_next_message("latency", event)
    assert result == events.ProjectCreated


def test_get_next_message_is_update_document():
    event = events.ProjectCreated(benchmark_id=1)
    result = model.get_next_message("latency", event)
    assert result == commands.UpdateDocument


def test_get_next_message_unknown_benchmark_type():
    with pytest.raises(NotImplementedError):
        # ignoring type to test NotImplementedError
        model.get_next_message("new_benchmark", "fake_event")  # type: ignore


def test_get_next_message_unassigned_event():
    class FakeEvent(events.Event):
        channel = "fake_event"

    fake_event = FakeEvent(channel="fake_channel", benchmark_id=1)

    with pytest.raises(MessageNotAssignedToBenchmarkError):
        model.get_next_message("latency", fake_event)

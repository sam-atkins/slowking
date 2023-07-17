from datetime import datetime, timedelta, timezone

import pytest

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


def test_latency_benchmark_next_message():
    lbm = model.LatencyBenchmark()
    assert lbm.next_message(events.BenchmarkCreated) == events.ProjectCreated
    assert lbm.next_message(events.ProjectCreated) == commands.UpdateDocument
    assert lbm.next_message(model.commands.UpdateDocument) == events.DocumentUpdated
    assert lbm.next_message(events.DocumentUpdated) == events.AllDocumentsUploaded
    assert lbm.next_message(events.AllDocumentsUploaded) is None


def test_latency_benchmark_next_message_unassigned_event():
    class FakeEvent(events.Event):
        channel = "fake_event"

    lbm = model.LatencyBenchmark()
    with pytest.raises(MessageNotAssignedToBenchmarkError):
        lbm.next_message(FakeEvent)


def test_get_benchmark_types():
    result = model.BenchmarkTypesEnum.get_benchmark_types()
    assert result == ["latency"]


def test_get_next_message():
    result = model.get_next_message(
        model.BenchmarkTypesEnum.LATENCY, events.BenchmarkCreated
    )
    assert result == events.ProjectCreated
    result = model.get_next_message(
        model.BenchmarkTypesEnum.LATENCY, events.ProjectCreated
    )
    assert result == commands.UpdateDocument


def test_get_next_message_unknown_benchmark_type():
    with pytest.raises(NotImplementedError):
        # ignoring type to test NotImplementedError
        model.get_next_message("new_benchmark", "fake_event")  # type: ignore


def test_get_next_message_unassigned_event():
    class FakeEvent(events.Event):
        channel = "fake_event"

    with pytest.raises(MessageNotAssignedToBenchmarkError):
        model.get_next_message(model.BenchmarkTypesEnum.LATENCY, FakeEvent)

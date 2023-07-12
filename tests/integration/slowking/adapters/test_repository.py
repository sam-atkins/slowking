# import pytest

from slowking.adapters import repository
from slowking.domain import model

# pytestmark = pytest.mark.usefixtures("mappers")


def test_get_by_id(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.SqlAlchemyRepository(session)
    docs = [model.Document(name="doc test", file_path="path/to/file")]
    project = model.Project(
        name="test project",
        document=docs,
    )
    benchmark = model.Benchmark(
        name="test benchmark",
        benchmark_type="latency test",
        eigen_platform_version="v1.0.0",
        target_infra="kubernetes",
        target_url="http://localhost:8080",
        username="test_user",
        password="test_password",
        project=project,
    )
    repo.add(benchmark)
    assert repo.get_by_id(1) == benchmark


def test_get_by_name(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.SqlAlchemyRepository(session)
    docs = [model.Document(name="doc test", file_path="path/to/file")]
    project = model.Project(
        name="test project",
        document=docs,
    )
    benchmark = model.Benchmark(
        name="latency benchmark for release 1.0.0",
        benchmark_type="latency test",
        eigen_platform_version="v1.0.0",
        target_infra="kubernetes",
        target_url="http://localhost:8080",
        username="test_user",
        password="test_password",
        project=project,
    )
    repo.add(benchmark)
    assert repo.get_by_name("latency benchmark for release 1.0.0") == benchmark


def test_get_by_host_and_project_id(sqlite_session_factory):
    session = sqlite_session_factory()
    repo = repository.SqlAlchemyRepository(session)
    docs = [model.Document(name="doc test", file_path="path/to/file")]
    project = model.Project(
        name="test project",
        document=docs,
        eigen_project_id=20,
    )
    benchmark = model.Benchmark(
        name="latency benchmark for release 1.0.0",
        benchmark_type="latency test",
        eigen_platform_version="v1.0.0",
        target_infra="kubernetes",
        target_url="http://localhost:8081",
        username="test_user",
        password="test_password",
        project=project,
    )
    repo.add(benchmark)
    assert (
        repo.get_by_host_and_project_id(host="http://localhost:8081", project_id=20)
        == benchmark
    )

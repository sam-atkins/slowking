"""
Note these tests pass when running the entire test suite
but do not pass when running just this module.
The error is `UnmappedInstanceError`.
"""
import pytest

from slowking.adapters import repository

pytestmark = pytest.mark.usefixtures("mappers")


def test_get_by_id(sqlite_session_factory, benchmark):
    session = sqlite_session_factory()
    repo = repository.SqlAlchemyRepository(session)
    repo.add(benchmark)
    assert repo.get_by_id(1) == benchmark


def test_get_by_name(sqlite_session_factory, benchmark):
    session = sqlite_session_factory()
    repo = repository.SqlAlchemyRepository(session)
    repo.add(benchmark)
    assert repo.get_by_name("latency benchmark for release 1.0.0") == benchmark


def test_get_by_host_and_project_id(sqlite_session_factory, benchmark):
    session = sqlite_session_factory()
    repo = repository.SqlAlchemyRepository(session)
    repo.add(benchmark)
    assert (
        repo.get_by_host_and_project_id(host="http://localhost:8080", project_id=20)
        == benchmark
    )

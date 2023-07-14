from slowking.domain import model
from slowking.service_layer import unit_of_work


def get_benchmark_by_name(session, name):
    benchmark = session.query(model.Benchmark).filter_by(name=name).first()
    return benchmark


def test_uow_adds_benchmark(sqlite_session_factory, benchmark):
    uow = unit_of_work.SqlAlchemyUnitOfWork(sqlite_session_factory)
    with uow:
        uow.benchmarks.add(benchmark)

    session = sqlite_session_factory()
    benchmark = get_benchmark_by_name(session, "latency benchmark for release 1.0.0")
    assert benchmark is not None
    assert benchmark.name == "latency benchmark for release 1.0.0"

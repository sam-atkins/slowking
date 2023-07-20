import uuid
from collections import defaultdict
from datetime import datetime, timezone

from slowking import bootstrap
from slowking.adapters import notifications, repository
from slowking.adapters.http import EigenClient, ProjectStruct
from slowking.domain import commands, events, model
from slowking.service_layer import unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, benchmarks):
        super().__init__()
        self._benchmarks = set(benchmarks)

    def _add(self, benchmark):
        # add a fake id to the benchmark
        benchmark.id = len(self._benchmarks) + 1
        self._benchmarks.add(benchmark)

    def _get_by_id(self, id):
        return next((b for b in self._benchmarks if b.id == id), None)

    def _get_by_name(self, name):
        return next((b for b in self._benchmarks if b.name == name), None)

    def _get_by_host_and_project_id(self, host: str, project_id: int):
        # implement if needed
        pass


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.benchmarks = FakeRepository([])
        self.committed = False
        self.flushed = False
        self.rolled_back = False

    def _commit(self):
        self.committed = True

    def _rollback(self):
        self.rolled_back = True

    def _flush(self):
        self.flushed = True

    def rollback(self):
        self.rollback()


class FakeNotifications(notifications.AbstractNotifications):
    def __init__(self):
        self.sent = defaultdict(list)

    def send(self, benchmark: model.Benchmark, message: str):
        destination = ["test@example.com"]
        self.sent[destination].append(message)


class FakeClient(EigenClient):
    def __init__(self, *args, **kwargs):
        pass

    def create_project(self, *args, **kwargs):
        response = ProjectStruct(
            document_type_id=123,
            guid=str(uuid.uuid4()),
            name="test",
            description="test",
            created_at=datetime.now(tz=timezone.utc).isoformat(),
            language="en",
            use_numerical_confidence_predictions=True,
        )
        return response


def bootstrap_test_app():
    return bootstrap.bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork(),
        notifications=FakeNotifications(),
        publish=lambda *args: None,
        client=FakeClient,
    )


def test_create_benchmark():
    bus = bootstrap_test_app()
    bus.handle(
        commands.CreateBenchmark(
            channel=commands.CommandChannelEnum.CREATE_BENCHMARK,
            name="test",
            benchmark_type="latency",
            target_infra="k8s",
            target_url="http://localhost:8080",
            target_eigen_platform_version="0.0.1",
            username="test",
            password="secret_pw",
        )
    )
    assert bus.uow.benchmarks.get_by_id(1) is not None
    assert bus.uow.committed  # type: ignore


def test_create_project():
    bus = bootstrap_test_app()
    bus.handle(
        commands.CreateBenchmark(
            channel=commands.CommandChannelEnum.CREATE_BENCHMARK,
            name="test",
            benchmark_type="latency",
            target_infra="k8s",
            target_url="http://localhost:8080",
            target_eigen_platform_version="0.0.1",
            username="test",
            password="secret_pw",
        )
    )
    benchmark = bus.uow.benchmarks.get_by_id(1)
    assert benchmark is not None

    bus.handle(events.BenchmarkCreated(benchmark_id=1))
    # this is the project id returned from the fake client
    assert benchmark.project.eigen_project_id == 123
    assert bus.uow.committed  # type: ignore

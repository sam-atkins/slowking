from collections import defaultdict

from pydantic import SecretStr

from slowking import bootstrap
from slowking.adapters import notifications, repository
from slowking.domain import commands
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

    def send(self, destination, message):
        self.sent[destination].append(message)


def bootstrap_test_app():
    return bootstrap.bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork(),
        notifications=FakeNotifications(),
        publish=lambda *args: None,
    )


def test_create_benchmark():
    secret_pw = SecretStr("test")
    bus = bootstrap_test_app()
    bus.handle(
        commands.CreateBenchmark(
            channel=commands.CommandChannelEnum.CREATE_BENCHMARK,
            name="test",
            benchmark_type="latency_test",
            target_infra="k8s",
            target_url="http://localhost:8080",
            target_eigen_platform_version="0.0.1",
            username="test",
            password=secret_pw,
        )
    )
    assert bus.uow.benchmarks.get_by_id(1) is not None
    assert bus.uow.committed  # type: ignore

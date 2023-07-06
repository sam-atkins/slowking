"""
Repository adapters
"""
import abc

from slowking.adapters import orm
from slowking.domain import model


class AbstractRepository(abc.ABC):
    def __init__(self):
        pass

    def add(self, benchmark: model.Benchmark) -> model.Benchmark:
        return self._add(benchmark)

    def get_by_id(self, id: int) -> model.Benchmark:
        benchmark = self._get_by_id(id)
        return benchmark

    def get_by_name(self, name: str) -> model.Benchmark:
        benchmark = self._get_by_name(name)
        return benchmark

    def get_by_host_and_project_id(self, host: str, project_id: str) -> model.Benchmark:
        benchmark = self._get_by_host_and_project_id(host, project_id)
        return benchmark

    @abc.abstractmethod
    def _add(self, benchmark: model.Benchmark) -> model.Benchmark:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_id(self, id) -> model.Benchmark:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_name(self, name) -> model.Benchmark:
        raise NotImplementedError

    @abc.abstractclassmethod
    def _get_by_host_and_project_id(
        self, host: str, project_id: str
    ) -> model.Benchmark:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, benchmark) -> model.Benchmark:
        return self.session.add(benchmark)

    def _get_by_id(self, id) -> model.Benchmark:
        return self.session.query(model.Benchmark).filter_by(id=id).first()

    def _get_by_name(self, name) -> model.Benchmark:
        return self.session.query(model.Benchmark).filter_by(name=name).first()

    def _get_by_host_and_project_id(
        self, host: str, project_id: str
    ) -> model.Benchmark:
        return (
            self.session.query(model.Benchmark)
            .join(model.Project)
            .filter(
                orm.benchmark.c.target_url == host,
                orm.project.c.eigen_project_id == project_id,
            )
            .first()
        )

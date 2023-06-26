"""
Repository adapters
"""
import abc
from typing import Set  # noqa: F401

from src.domain import model


class AbstractRepository(abc.ABC):
    def __init__(self):
        # is this needed? need to understand the purpose of seen events
        self.seen = set()  # type: Set[model.Benchmark]

    def add(self, benchmark: model.Benchmark):
        self._add(benchmark)
        self.seen.add(benchmark)

    def get(self, name) -> model.Benchmark:
        benchmark = self._get(name)
        if benchmark:
            self.seen.add(benchmark)
        return benchmark

    # get by ? project? target_instance?
    # def get_by_batchref(self, batchref) -> model.Benchmark:
    #     benchmark = self._get_by_batchref(batchref)
    #     if benchmark:
    #         self.seen.add(benchmark)
    #     return benchmark

    @abc.abstractmethod
    def _add(self, benchmark: model.Benchmark):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, sku) -> model.Benchmark:
        raise NotImplementedError

    # @abc.abstractmethod
    # def _get_by_batchref(self, batchref) -> model.Benchmark:
    #     raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, benchmark):
        self.session.add(benchmark)

    def _get(self, name):
        return self.session.query(model.Benchmark).filter_by(name=name).first()

    # def _get_by_batchref(self, batchref):
    #     return (
    #         self.session.query(model.Benchmark)
    #         .join(model.Batch)
    #         .filter(
    #             orm.batches.c.reference == batchref,
    #         )
    #         .first()
    #     )

from __future__ import annotations

import abc

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from src.adapters import repository
from src.config import settings

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        settings.SQLALCHEMY_DATABASE_URI,  # type: ignore
        isolation_level="REPEATABLE READ",
    )
)


class AbstractUnitOfWork(abc.ABC):
    benchmarks: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def flush(self):
        self._flush()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _flush(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory: sessionmaker[Session] = session_factory

    def __enter__(self):
        self.session: Session = self.session_factory()
        self.benchmarks = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def _flush(self):
        self.session.flush()

    def rollback(self):
        self.session.rollback()

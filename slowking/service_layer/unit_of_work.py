from __future__ import annotations

import abc
import logging.config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from slowking.adapters import repository
from slowking.config import settings

logger = logging.getLogger(__name__)

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

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self._rollback()
            return

        self._commit()

    def flush(self):
        self._flush()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _flush(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """
    Unit of Work for SQLAlchemy
    """

    # benchmarks: repository.AbstractRepository

    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session: Session = self.session_factory()
        self.benchmarks = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def _flush(self):
        self.session.flush()

    def _rollback(self):
        self.session.rollback()

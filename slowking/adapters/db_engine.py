import sqlalchemy as db
from pydantic import PostgresDsn
from sqlalchemy.engine.base import Engine

from slowking.adapters.orm import metadata


def get_engine(db_uri: str) -> Engine:
    engine = db.create_engine(db_uri, pool_pre_ping=True)
    return engine


def init_db(db_uri: PostgresDsn, echo: bool = False):
    engine = get_engine(db_uri)
    # this creates all the tables
    # ideally replace with Alembic
    metadata.create_all(engine)
    engine.dispose()
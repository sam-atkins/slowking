import sqlalchemy as db
from sqlalchemy.engine.base import Engine

from src.adapters.orm import metadata


def get_engine(db_uri: str) -> Engine:
    engine = db.create_engine(db_uri, pool_pre_ping=True)
    return engine


def init_db(db_uri: str, echo: bool = False):
    engine = get_engine(db_uri)
    # this creates all the tables
    # ideally replace with Alembic
    metadata.create_all(engine)
    engine.dispose()

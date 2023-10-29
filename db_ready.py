#!/usr/bin/env python3
from time import sleep

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from slowking.config import settings

RETRIES = 10
WAIT_FIXED = 3


def db_ready():
    """Check if the database is ready"""
    print("Checking if the database is ready...")
    for _ in range(RETRIES):
        try:
            engine = create_engine(
                settings.SQLALCHEMY_DATABASE_URI,  # type: ignore
                pool_pre_ping=True,
            )
            with engine.connect() as conn:
                txt = text("SELECT 1")
                conn.execute(txt)
            print("Database is ready")
            break
        except OperationalError:
            print("Database is not ready")
            sleep(WAIT_FIXED)


db_ready()

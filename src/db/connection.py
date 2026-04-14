"""
Database connection helpers.
"""

from contextlib import contextmanager
from typing import Iterator
import pymysql
from pymysql.cursors import DictCursor

from ..config.settings import Settings


@contextmanager
def get_db_connection(settings):
    """Open a short-lived MySQL connection configured for UTF-8 content."""

    connection = pymysql.connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=True,
    )
    try:
        yield connection
    finally:
        connection.close()

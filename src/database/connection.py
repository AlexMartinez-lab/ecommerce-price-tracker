"""PostgreSQL connection utilities."""

from collections.abc import Generator
from contextlib import contextmanager


import psycopg
from psycopg import Connection
from psycopg.rows import dict_row


from src.database.config import database_config


def create_connection() -> Connection:
	"""
	Create and return a PostgreSQL connection.

	The caller is responsible for closing the returned connection.
	"""

	return psycopg.connect(
		host=database_config.host,
		port=database_config.port,
		dbname=database_config.name,
		user=database_config.user,
		password=database_config.password,
		row_factory=dict_row,
		connect_timeout=10,
	)


@contextmanager
def database_connection() -> Generator[Connection, None, None]:
	"""
	Provide a managed PostgreSQL connection.

	The transaction is committed when the context finishes successfully.
	It is rolled back automatically if an exception occurs.
	The connection is always closed.
	"""

	connection = create_connection()

	try:
		with connection:
			yield connection
	finally:
		connection.close()

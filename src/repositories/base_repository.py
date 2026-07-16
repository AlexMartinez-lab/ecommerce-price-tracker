"""Common functionality for repository classes."""


from typing import Any

from psycopg.rows import DictRow

from src.database.connection import database_connection



class BaseRepository:
	"""Provide reusable methods for PostgreSQL repositories."""


	@staticmethod
	def fetch_one(
		query: str,
		parameters: tuple[Any, ...] | None = None,
	) -> DictRow | None:
		"""Execute a query and return one row."""


		with database_connection() as connection:
			with connection.cursor() as cursor:
				cursor.execute(query, parameters)
				return cursor.fetchone()

	@staticmethod
	def fetch_all(
		query: str,
		parameters: tuple[Any, ...] | None = None,
	) -> list[DictRow]:
		"""Execute a query and return all rows."""


		with database_connection() as connection:
			with connection.cursor() as cursor:
				cursor.execute(query, parameters)
				return cursor.fetchall()


	@staticmethod
	def execute(
		query: str,
		parameters: tuple[Any, ...] | None = None,
	) -> int:
		"""Execute a data modification query and return affected rows."""


		with database_connection() as connection:
			with connection.cursor() as cursor:
				cursor.execute(query, parameters)
				return cursor.rowcount

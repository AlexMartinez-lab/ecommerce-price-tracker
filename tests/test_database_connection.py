"""Integration tests for the PostgreSQL connection. """

import unittest

from src.database.connection import database_connection


class DatabaseConnectionTestCase(unittest.TestCase):
	"""Validate access to the project database."""

	def test_database_returns_expected_name(self) -> None:
		"""The connection must be use the price_tracker database."""

		with database_connection() as connection:
			with connection.cursor() as cursor:
				cursor.execute(
					"SELECT current_database() AS database_name;"
				)
				result = cursor.fetchone()


		self.assertEqual(
			result["database_name"],
			"price_tracker",
		)

	def test_required_tables_exist(self) -> None:
		"""The initial MVP table must exist."""

		query = """
			SELECT table_name
			FROM information_schema.tables
			WHERE table_schema = 'public';
		"""

		expected_tables = {
			"products",
			"stores",
			"product_listings",
			"pipeline_runs",
			"price_history",
		}


		with database_connection() as connection:
			with connection.cursor() as cursor:
				cursor.execute(query)
				results = cursor.fetchall()

		existing_tables = {
			result["table_name"]
			for result in results
		}

		self.assertTrue(
			expected_tables.issubset(existing_tables)
		)


if __name__ == '__main__':
	unittest.main()

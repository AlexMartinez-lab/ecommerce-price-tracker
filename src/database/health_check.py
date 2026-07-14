"""Dadabase connection health check."""


import sys

import psycopg

from src.database.connection import database_connection


def check_database_connection() -> bool:
	"""
	Verify the PostgreSQL connection and required project tables.

	Returns:
		True when the connection and schema are available.
		False when the validation fails.
	"""


	query = """
		SELECT
			current_database() AS database_name,
			current_user AS database_user,
			version() AS postgres_version;
		"""

	tables_query = """
		SELECT table_name
		FROM information_schema.tables
		WHERE table_schema = 'public'
			AND table_name IN (
				'products',
				'stores',
				'product_listings',
				'pipeline_runs',
				'price_history'
			)
		ORDER BY table_name;
	"""


	try:
		with database_connection() as connection:
			with connection.cursor() as cursor:
				cursor.execute(query)
				database_info = cursor.fetchone()

				cursor.execute(tables_query)
				table_rows = cursor.fetchall()

		existing_tables = {
			row["table_name"]
			for row in table_rows
		}

		required_tables = {
			"products",
			"stores",
			"product_listings",
			"pipeline_runs",
			"price_history"
		}


		missing_tables = required_tables - existing_tables

		print("Database connection successful.")
		print(f"Database: {database_info['database_name']}")
		print(f"User: {database_info['database_user']}")
		print(f"Detected tables: {len(existing_tables)}")


		if missing_tables:
			print(
				"Missing tables: "
				+ ", ".join(sorted(missing_tables))
			)
			return False

		print("Database schema validation successful.")
		return True


	except psycopg.OperationalError as error:
		print("Unable to connect to PostgreSQL.")
		print(f"Database error: {error}")
		return False

	except psycopg.Error as error:
		print("A PostgreSQL operation failed.")
		print(f"Database error: {error}")
		return False


def main() -> None:
	"""Run the health check as a command-line module."""

	connection_is_healthy = check_database_connection()

	if not connection_is_healthy:
		sys.exit(1)

if __name__ == "__main__":
	main()

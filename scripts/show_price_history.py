"""Display the current development price history."""


from decimal import Decimal
from typing import Any


from src.database.connection import database_connection


PRICE_HISTORY_QUERY = """
	SELECT
		p.name AS product_name,
		s.name AS store_name,
		pl.title AS listing_title,
		ph.current_price,
		ph.currency,
		ph.available,
		ph.observed_at
	FROM price_history AS ph
	INNER JOIN product_listings AS pl
		ON ph.listing_id = pl.id
	INNER JOIN products AS p
		ON pl.product_id = p.id
	INNER JOIN stores AS s
		ON pl.store_id = s.id
	ORDER BY  ph. observed_at DESC;
"""



def format_price(price: Decimal, currency: str) -> str:
	"""Format a monetary value for terminal output."""

	return f"${price:,.2f} {currency}"


def display_observation(row: dict[str, Any]) -> None:
	"""Display one price observation."""

	availability = "Available" if row["available"] else "Unavailable"

	print("-" * 60)
	print(f"Product: {row['product_name']}")
	print(f"Store: {row['store_name']}")
	print(f"Listing: {row['listing_title']}")
	print(
		"Price: "
		f"{format_price(row['current_price'], row['currency'])}"
	)
	print(f"Status: {availability}")
	print(f"Observed at: {row['observed_at']}")


def main() -> None:
	"""Retrieve and display all price observations."""

	with database_connection() as connection:
		with connection.cursor() as cursor:
			cursor.execute(PRICE_HISTORY_QUERY)
			observations = cursor.fetchall()

	if not observations:
		print("No price observations were found.")
		return

	print(f"Price observations found: {len(observations)}")

	for observation in observations:
		display_observation(observation)


if __name__ == '__main__':
	main()

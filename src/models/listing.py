""" Product listing domain model."""


from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ProductListing:
	"""Represent one store-specific publication."""


	product_id: int
	store_id: int
	title: str
	url: str
	external_listing_id: str | None = None
	image_url: str | None = None
	condition: str = "unknown"
	active: bool = True
	id: int | None = None
	first_seen_at: datetime | None = None
	last_seen_at: datetime | None = None
	created_at: datetime | None = None
	updated_at: datetime | None = None


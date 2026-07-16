""" Store domain model."""


from dataclasses import dataclass
from datetime import datetime



@dataclass(slots=True)
class Store:
	"""Represent an e-commerce website or marketplace."""


	name: str
	domain: str
	country_code: str = "MX"
	active: bool = True
	id: int | None = None
	created_at: datetime | None = None
	updated_at: datetime | None = None


"""Product domain model."""


from dataclasses import dataclass
from datetime import datetime



@dataclass(slots=True)
class Product:
	"""Represent a canonical product tracked by the system."""


	name: str
	brand: str | None = None
	model: str | None = None
	sku: str | None = None
	description: str | None = None
	active: bool = True
	id: int | None = None
	created_at: datetime | None = None
	updated_at: datetime | None = None

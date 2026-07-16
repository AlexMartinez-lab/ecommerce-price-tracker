"""Price observation domain model."""


from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal



@dataclass(slots=True)
class PriceObservation:
	"""Represent one historical listing observation."""


	listing_id: int
	current_price: Decimal
	observed_at: datetime
	pipeline_run_id: int | None = None
	original_price: Decimal | None = None
	shipping_cost: Decimal | None = None
	currency: str = "MXN"
	available: bool = True
	stock_status: str | None = None
	raw_price_text: str | None = None
	id: int | None = None
	created_at: datetime | None = None

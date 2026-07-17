"""Models returned by product data collectors."""


from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CollectedProductData:
	"""Represent normalized product data extracted from a source."""


	external_listing_id: str
	title: str
	current_price: Decimal
	currency: str
	available: bool

	original_price: Decimal | None = None
	shipping_cost: Decimal | None = None
	stock_status: str | None = None
	brand: str | None = None
	model: str | None = None
	image_url: str | None = None
	raw_price_text: str | None = None
 
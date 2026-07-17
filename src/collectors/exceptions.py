"""Exceptions raised by data collection adapters."""


class CollectionError(Exception):
	"""Base exception for data collection failures."""


class SourceReadError(CollectionError):
	"""Raised when a source cannot be read."""


class ElementNotFoundError(CollectionError):
	"""Raised when a required HTML element is missing."""


class InvalidPriceError(CollectionError):
	"""Raised when a price cannot be normalized."""

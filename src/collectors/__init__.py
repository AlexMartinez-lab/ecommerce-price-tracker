"""Data collection components exposed by the application."""

from src.collectors.base import ProductCollector
from src.collectors.local_html_adapter import (
    LocalHtmlCollector,
)
from src.collectors.models import CollectedProductData

__all__ = [
    "CollectedProductData",
    "LocalHtmlCollector",
    "ProductCollector",
]
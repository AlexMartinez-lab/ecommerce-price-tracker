"""Base interface for product data collection adapters."""

from abc import ABC, abstractmethod

from src.collectors.models import CollectedProductData


class ProductCollector(ABC):
    """Define the interface implemented by product collectors."""

    @abstractmethod
    def collect(self) -> CollectedProductData:
        """
        Collect and normalize product information.

        Returns:
            Normalized product data.
        """
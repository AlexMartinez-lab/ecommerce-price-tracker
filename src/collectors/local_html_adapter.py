"""Product collector for a controlled local HTML fixture."""
from decimal import Decimal
from pathlib import Path

from bs4 import BeautifulSoup
from bs4.element import Tag

from src.collectors.base import ProductCollector
from src.collectors.exceptions import (
    ElementNotFoundError,
    SourceReadError,
)
from src.collectors.models import CollectedProductData
from src.collectors.price_parser import parse_price


class LocalHtmlCollector(ProductCollector):
    """Collect product data from a local HTML file."""

    def __init__(self, html_file: Path) -> None:
        """
        Initialize the collector.

        Args:
            html_file: Path to the HTML source.
        """

        self.html_file = html_file

    def collect(self) -> CollectedProductData:
        """Read, parse and normalize the local product page."""

        html_content = self._read_source()
        soup = BeautifulSoup(html_content, "html.parser")

        product_element = self._require_element(
            soup,
            ".product",
        )

        external_listing_id = self._require_attribute(
            product_element,
            "data-listing-id",
        )

        title_element = self._require_element(
            soup,
            ".product__title",
        )

        current_price_element = self._require_element(
            soup,
            ".product__current-price",
        )

        currency_element = self._require_element(
            soup,
            ".product__currency",
        )

        availability_element = self._require_element(
            soup,
            ".product__availability",
        )

        raw_current_price = current_price_element.get_text(
            strip=True
        )

        original_price_element = soup.select_one(
            ".product__original-price"
        )

        shipping_element = soup.select_one(
            ".product__shipping"
        )

        brand_element = soup.select_one(
            ".product__brand"
        )

        model_element = soup.select_one(
            ".product__model"
        )

        image_element = soup.select_one(
            ".product__image"
        )

        original_price = None

        if original_price_element is not None:
            original_price = parse_price(
                original_price_element.get_text(strip=True)
            )

        shipping_cost = self._parse_shipping_cost(
            shipping_element
        )

        image_url = None

        if isinstance(image_element, Tag):
            image_url = image_element.get("src")

        available_attribute = availability_element.get(
            "data-available",
            "false",
        )

        available = (
            str(available_attribute).strip().lower() == "true"
        )

        return CollectedProductData(
            external_listing_id=external_listing_id,
            title=title_element.get_text(strip=True),
            current_price=parse_price(raw_current_price),
            original_price=original_price,
            shipping_cost=shipping_cost,
            currency=currency_element.get_text(
                strip=True
            ).upper(),
            available=available,
            stock_status=availability_element.get_text(
                strip=True
            ),
            brand=self._optional_text(brand_element),
            model=self._optional_text(model_element),
            image_url=(
                str(image_url)
                if image_url is not None
                else None
            ),
            raw_price_text=raw_current_price,
        )

    def _read_source(self) -> str:
        """Read the configured HTML source."""

        try:
            return self.html_file.read_text(
                encoding="utf-8"
            )
        except OSError as error:
            raise SourceReadError(
                f"Unable to read source: {self.html_file}"
            ) from error

    @staticmethod
    def _require_element(
        soup: BeautifulSoup,
        selector: str,
    ) -> Tag:
        """Return a required element or raise an error."""

        element = soup.select_one(selector)

        if not isinstance(element, Tag):
            raise ElementNotFoundError(
                f"Required element not found: {selector}"
            )

        return element

    @staticmethod
    def _require_attribute(
        element: Tag,
        attribute: str,
    ) -> str:
        """Return a required HTML attribute."""

        value = element.get(attribute)

        if value is None or str(value).strip() == "":
            raise ElementNotFoundError(
                f"Required attribute not found: {attribute}"
            )

        return str(value).strip()

    @staticmethod
    def _optional_text(element: Tag | None) -> str | None:
        """Return normalized text from an optional element."""

        if element is None:
            return None

        value = element.get_text(strip=True)

        return value if value else None

    @staticmethod
    def _parse_shipping_cost(
        shipping_element: Tag | None,
    ) -> Decimal | None:
        """Parse the shipping cost from optional text."""

        if shipping_element is None:
            return None

        shipping_text = shipping_element.get_text(
            strip=True
        )

        normalized_text = shipping_text.lower()

        if "gratis" in normalized_text:
            return parse_price("0.00")

        return parse_price(shipping_text)
"""Tests for the controlled local HTML collector."""

import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from src.collectors.exceptions import (
    ElementNotFoundError,
    SourceReadError,
)
from src.collectors.local_html_adapter import (
    LocalHtmlCollector,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

HTML_FIXTURE = (
    PROJECT_ROOT
    / "data"
    / "fixtures"
    / "sample_product.html"
)


class LocalHtmlCollectorTestCase(unittest.TestCase):
    """Validate product extraction from controlled HTML."""

    def test_collect_complete_product_data(self) -> None:
        """The fixture must produce normalized product data."""

        collector = LocalHtmlCollector(HTML_FIXTURE)

        product = collector.collect()

        self.assertEqual(
            product.external_listing_id,
            "DEMO-RTX5070TI-001",
        )

        self.assertEqual(
            product.title,
            "MSI GeForce RTX 5070 Ti 16G Gaming Trio OC",
        )

        self.assertEqual(
            product.current_price,
            Decimal("21499.00"),
        )

        self.assertEqual(
            product.original_price,
            Decimal("24999.00"),
        )

        self.assertEqual(
            product.shipping_cost,
            Decimal("0.00"),
        )

        self.assertEqual(product.currency, "MXN")
        self.assertTrue(product.available)
        self.assertEqual(product.brand, "MSI")

    def test_missing_file_raises_source_error(self) -> None:
        """A missing source file must produce a controlled error."""

        collector = LocalHtmlCollector(
            Path("/tmp/nonexistent-product-page.html")
        )

        with self.assertRaises(SourceReadError):
            collector.collect()

    def test_missing_required_element_raises_error(self) -> None:
        """Missing required selectors must be reported."""

        invalid_html = """
            <html>
                <body>
                    <article class="product"></article>
                </body>
            </html>
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            html_file = Path(temp_dir) / "invalid.html"

            html_file.write_text(
                invalid_html,
                encoding="utf-8",
            )

            collector = LocalHtmlCollector(html_file)

            with self.assertRaises(
                ElementNotFoundError
            ):
                collector.collect()


if __name__ == "__main__":
    unittest.main()
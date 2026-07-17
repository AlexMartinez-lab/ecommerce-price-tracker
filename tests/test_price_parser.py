"""Unit tests for monetary value normalization."""

import unittest
from decimal import Decimal

from src.collectors.exceptions import InvalidPriceError
from src.collectors.price_parser import parse_price


class PriceParserTestCase(unittest.TestCase):
    """Validate supported price formats."""

    def test_mexican_price_format(self) -> None:
        """Currency symbols and thousands separators are removed."""

        result = parse_price("$21,499.00")

        self.assertEqual(
            result,
            Decimal("21499.00"),
        )

    def test_price_without_currency_symbol(self) -> None:
        """Plain numeric strings are accepted."""

        result = parse_price("999.99")

        self.assertEqual(
            result,
            Decimal("999.99"),
        )

    def test_comma_decimal_format(self) -> None:
        """European-style separators are normalized."""

        result = parse_price("21.499,50")

        self.assertEqual(
            result,
            Decimal("21499.50"),
        )

    def test_integer_with_thousands_separator(self) -> None:
        """A comma followed by three digits is treated as thousands."""

        result = parse_price("21,499")

        self.assertEqual(
            result,
            Decimal("21499"),
        )

    def test_empty_price_raises_error(self) -> None:
        """Empty price text is invalid."""

        with self.assertRaises(InvalidPriceError):
            parse_price("")

    def test_non_numeric_price_raises_error(self) -> None:
        """Text without a numeric value is invalid."""

        with self.assertRaises(InvalidPriceError):
            parse_price("Not available")

    def test_negative_price_raises_error(self) -> None:
        """Negative monetary values are rejected."""

        with self.assertRaises(InvalidPriceError):
            parse_price("-100.00")


if __name__ == "__main__":
    unittest.main()
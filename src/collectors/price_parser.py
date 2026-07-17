"""Utilities for normalizing monetary values."""

import re
from decimal import Decimal, InvalidOperation

from src.collectors.exceptions import InvalidPriceError


PRICE_CLEANING_PATTERN = re.compile(r"[^\d,.\-]")


def parse_price(raw_price: str) -> Decimal:
    """
    Convert a displayed price into a Decimal value.

    Supported examples:

    - $21,499.00
    - 21499.00
    - MXN 21,499
    - 21 499,50

    Args:
        raw_price: Price text extracted from a source.

    Returns:
        Normalized Decimal value.

    Raises:
        InvalidPriceError: If the price cannot be converted.
    """

    if raw_price is None or raw_price.strip() == "":
        raise InvalidPriceError("Price text cannot be empty.")

    cleaned_value = PRICE_CLEANING_PATTERN.sub(
        "",
        raw_price.strip(),
    )

    normalized_value = _normalize_separators(cleaned_value)

    try:
        price = Decimal(normalized_value)
    except InvalidOperation as error:
        raise InvalidPriceError(
            f"Invalid price value: {raw_price!r}"
        ) from error

    if price < 0:
        raise InvalidPriceError(
            "Price values cannot be negative."
        )

    return price


def _normalize_separators(value: str) -> str:
    """
    Normalize common decimal and thousands separators.

    This function supports common formats used in Mexico and
    international stores.
    """

    if value == "":
        raise InvalidPriceError(
            "Price contains no numeric characters."
        )

    has_comma = "," in value
    has_period = "." in value

    if has_comma and has_period:
        last_comma = value.rfind(",")
        last_period = value.rfind(".")

        if last_period > last_comma:
            return value.replace(",", "")

        return value.replace(".", "").replace(",", ".")

    if has_comma:
        decimal_digits = len(value) - value.rfind(",") - 1

        if decimal_digits in {1, 2}:
            return value.replace(",", ".")

        return value.replace(",", "")

    return value
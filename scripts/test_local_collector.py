"""Manual validation for the controlled HTML collector."""

from pathlib import Path

from src.collectors import LocalHtmlCollector


PROJECT_ROOT = Path(__file__).resolve().parents[1]

HTML_FIXTURE = (
    PROJECT_ROOT
    / "data"
    / "fixtures"
    / "sample_product.html"
)


def main() -> None:
    """Collect and display data from the sample product page."""

    collector = LocalHtmlCollector(HTML_FIXTURE)
    product_data = collector.collect()

    print("Controlled product collection successful.")
    print("-" * 60)
    print(
        f"Listing ID: "
        f"{product_data.external_listing_id}"
    )
    print(f"Title: {product_data.title}")
    print(f"Brand: {product_data.brand}")
    print(f"Model: {product_data.model}")
    print(
        f"Current price: "
        f"${product_data.current_price:,.2f} "
        f"{product_data.currency}"
    )

    if product_data.original_price is not None:
        print(
            f"Original price: "
            f"${product_data.original_price:,.2f} "
            f"{product_data.currency}"
        )

    if product_data.shipping_cost is not None:
        print(
            f"Shipping: "
            f"${product_data.shipping_cost:,.2f} "
            f"{product_data.currency}"
        )

    print(f"Available: {product_data.available}")
    print(f"Stock status: {product_data.stock_status}")
    print(f"Image: {product_data.image_url}")


if __name__ == "__main__":
    main()
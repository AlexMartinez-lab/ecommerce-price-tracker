"""Manual integration test for the data access layer."""

from datetime import datetime
from decimal import Decimal

from src.models import (
    PriceObservation,
    Product,
    ProductListing,
    Store,
)
from src.repositories import (
    ListingRepository,
    PipelineRepository,
    PriceHistoryRepository,
    ProductRepository,
    StoreRepository,
)


def main() -> None:
    """Run an end-to-end repository integration test."""

    product_repository = ProductRepository()
    store_repository = StoreRepository()
    listing_repository = ListingRepository()
    pipeline_repository = PipelineRepository()
    price_repository = PriceHistoryRepository()

    print("Starting data access layer test.")

    product = product_repository.create(
        Product(
            name="DAL Test Product",
            brand="Test Brand",
            model="DAL-001",
            description="Temporary integration test product.",
        )
    )

    print(f"Product created with ID: {product.id}")

    store = store_repository.get_by_domain(
        "dal-test-store.example"
    )

    if store is None:
        store = store_repository.create(
            Store(
                name="DAL Test Store",
                domain="dal-test-store.example",
                country_code="MX",
            )
        )

    print(f"Store available with ID: {store.id}")

    if product.id is None or store.id is None:
        raise RuntimeError("Product and store IDs are required.")

    listing = listing_repository.create(
        ProductListing(
            product_id=product.id,
            store_id=store.id,
            external_listing_id=f"DAL-TEST-{product.id}",
            title="DAL Test Product Listing",
            url="https://dal-test-store.example/product",
            condition="new",
        )
    )

    print(f"Listing created with ID: {listing.id}")

    pipeline_run = pipeline_repository.start(
        execution_source="test"
    )

    print(f"Pipeline run started with ID: {pipeline_run.id}")

    if listing.id is None or pipeline_run.id is None:
        raise RuntimeError(
            "Listing and pipeline run IDs are required."
        )

    observation = price_repository.create(
        PriceObservation(
            listing_id=listing.id,
            pipeline_run_id=pipeline_run.id,
            current_price=Decimal("999.99"),
            original_price=Decimal("1199.99"),
            shipping_cost=Decimal("0.00"),
            currency="MXN",
            available=True,
            stock_status="available",
            raw_price_text="$999.99",
            observed_at=datetime.now().astimezone(),
        )
    )

    print(
        "Price observation created with ID: "
        f"{observation.id}"
    )

    listing_repository.update_last_seen(listing.id)

    finished_run = pipeline_repository.finish(
        pipeline_run_id=pipeline_run.id,
        status="success",
        listings_processed=1, 
        successful_records=1,
        failed_records=0,
    )

    print(f"Pipeline run status: {finished_run.status}")

    latest_observation = price_repository.get_latest(
        listing.id
    )

    if latest_observation is None:
        raise RuntimeError(
            "The latest price observation was not found."
        )

    print(
        "Latest recorded price: "
        f"${latest_observation.current_price} "
        f"{latest_observation.currency}"
    )

    search_results = product_repository.search_by_name(
        "DAL Test"
    )

    print(f"Products found by search: {len(search_results)}")

    product_repository.disable(product.id)
    listing_repository.disable(listing.id)

    print("Test product and listing disabled.")
    print("Data access layer test completed successfully.")


if __name__ == "__main__":
    main()
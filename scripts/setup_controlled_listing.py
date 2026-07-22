"""Create the controlled product, store and listing."""

from src.models import Product, ProductListing, Store
from src.repositories import (
    ListingRepository,
    ProductRepository,
    StoreRepository,
)


CONTROLLED_STORE_DOMAIN = "demo-store.local"
CONTROLLED_LISTING_ID = "DEMO-RTX5070TI-001"


def find_existing_product(
    repository: ProductRepository,
) -> Product | None:
    """Find the controlled canonical product."""

    products = repository.search_by_name(
        "MSI GeForce RTX 5070 Ti 16G Gaming Trio OC"
    )

    for product in products:
        if (
            product.model
            == "RTX-5070-TI-GAMING-TRIO-OC"
        ):
            return product

    return None


def main() -> None:
    """Create controlled development records if needed."""

    product_repository = ProductRepository()
    store_repository = StoreRepository()
    listing_repository = ListingRepository()

    product = find_existing_product(
        product_repository
    )

    if product is None:
        product = product_repository.create(
            Product(
                name=(
                    "MSI GeForce RTX 5070 Ti "
                    "16G Gaming Trio OC"
                ),
                brand="MSI",
                model="RTX-5070-TI-GAMING-TRIO-OC",
                description=(
                    "Canonical product used by the "
                    "controlled ETL pipeline."
                ),
            )
        )

        print(
            f"Controlled product created: {product.id}"
        )
    else:
        print(
            f"Controlled product already exists: "
            f"{product.id}"
        )

    store = store_repository.get_by_domain(
        CONTROLLED_STORE_DOMAIN
    )

    if store is None:
        store = store_repository.create(
            Store(
                name="Controlled Demo Store",
                domain=CONTROLLED_STORE_DOMAIN,
                country_code="MX",
            )
        )

        print(
            f"Controlled store created: {store.id}"
        )
    else:
        print(
            f"Controlled store already exists: "
            f"{store.id}"
        )

    if product.id is None or store.id is None:
        raise RuntimeError(
            "Product and store IDs are required."
        )

    listing = listing_repository.get_by_external_id(
        store_id=store.id,
        external_listing_id=CONTROLLED_LISTING_ID,
    )

    if listing is None:
        listing = listing_repository.create(
            ProductListing(
                product_id=product.id,
                store_id=store.id,
                external_listing_id=(
                    CONTROLLED_LISTING_ID
                ),
                title=(
                    "MSI GeForce RTX 5070 Ti "
                    "16G Gaming Trio OC"
                ),
                url=(
                    "local://data/fixtures/"
                    "sample_product.html"
                ),
                image_url=(
                    "https://example.com/images/"
                    "rtx-5070-ti.jpg"
                ),
                condition="new",
            )
        )

        print(
            f"Controlled listing created: "
            f"{listing.id}"
        )
    else:
        print(
            f"Controlled listing already exists: "
            f"{listing.id}"
        )

    print("Controlled ETL records are ready.")


if __name__ == "__main__":
    main()
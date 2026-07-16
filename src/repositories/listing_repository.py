"""Data access operations for product listings."""

from typing import Any

from src.models.listing import ProductListing
from src.repositories.base_repository import BaseRepository


class ListingRepository(BaseRepository):
    """Manage store-specific product listings."""

    @staticmethod
    def _row_to_listing(
        row: dict[str, Any] | None,
    ) -> ProductListing | None:
        """Convert a database row into a ProductListing object."""

        if row is None:
            return None

        return ProductListing(
            id=row["id"],
            product_id=row["product_id"],
            store_id=row["store_id"],
            external_listing_id=row["external_listing_id"],
            title=row["title"],
            url=row["url"],
            image_url=row["image_url"],
            condition=row["condition"],
            active=row["active"],
            first_seen_at=row["first_seen_at"],
            last_seen_at=row["last_seen_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, listing: ProductListing) -> ProductListing:
        """Insert and return a product listing."""

        query = """
            INSERT INTO product_listings (
                product_id,
                store_id,
                external_listing_id,
                title,
                url,
                image_url,
                condition,
                active
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
        """

        row = self.fetch_one(
            query,
            (
                listing.product_id,
                listing.store_id,
                listing.external_listing_id,
                listing.title,
                listing.url,
                listing.image_url,
                listing.condition,
                listing.active,
            ),
        )

        created_listing = self._row_to_listing(row)

        if created_listing is None:
            raise RuntimeError("Listing creation returned no data.")

        return created_listing

    def get_by_id(self, listing_id: int) -> ProductListing | None:
        """Return one listing by its identifier."""

        query = """
            SELECT *
            FROM product_listings
            WHERE id = %s;
        """

        return self._row_to_listing(
            self.fetch_one(query, (listing_id,))
        )

    def get_by_external_id(
        self,
        store_id: int,
        external_listing_id: str,
    ) -> ProductListing | None:
        """Return a listing using its source identifier."""

        query = """
            SELECT *
            FROM product_listings
            WHERE store_id = %s
              AND external_listing_id = %s;
        """

        return self._row_to_listing(
            self.fetch_one(
                query,
                (store_id, external_listing_id),
            )
        )

    def get_active(self) -> list[ProductListing]:
        """Return all listings enabled for tracking."""

        query = """
            SELECT *
            FROM product_listings
            WHERE active = TRUE
            ORDER BY id;
        """

        rows = self.fetch_all(query)

        return [
            listing
            for row in rows
            if (listing := self._row_to_listing(row)) is not None
        ]

    def update_last_seen(self, listing_id: int) -> bool:
        """Update the last successful observation timestamp."""

        query = """
            UPDATE product_listings
            SET
                last_seen_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """

        return self.execute(query, (listing_id,)) == 1

    def disable(self, listing_id: int) -> bool:
        """Disable tracking for a listing."""

        query = """
            UPDATE product_listings
            SET
                active = FALSE,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND active = TRUE;
        """

        return self.execute(query, (listing_id,)) == 1
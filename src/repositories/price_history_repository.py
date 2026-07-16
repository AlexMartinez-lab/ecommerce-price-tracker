"""Data access operations for historical price observations."""

from typing import Any

from src.models.price_observation import PriceObservation
from src.repositories.base_repository import BaseRepository


class PriceHistoryRepository(BaseRepository):
    """Manage append-only price observations."""

    @staticmethod
    def _row_to_observation(
        row: dict[str, Any] | None,
    ) -> PriceObservation | None:
        """Convert a database row into a PriceObservation object."""

        if row is None:
            return None

        return PriceObservation(
            id=row["id"],
            listing_id=row["listing_id"],
            pipeline_run_id=row["pipeline_run_id"],
            current_price=row["current_price"],
            original_price=row["original_price"],
            shipping_cost=row["shipping_cost"],
            currency=row["currency"],
            available=row["available"],
            stock_status=row["stock_status"],
            raw_price_text=row["raw_price_text"],
            observed_at=row["observed_at"],
            created_at=row["created_at"],
        )

    def create(
        self,
        observation: PriceObservation,
    ) -> PriceObservation:
        """Insert and return an immutable price observation."""

        query = """
            INSERT INTO price_history (
                listing_id,
                pipeline_run_id,
                current_price,
                original_price,
                shipping_cost,
                currency,
                available,
                stock_status,
                raw_price_text,
                observed_at
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING *;
        """

        row = self.fetch_one(
            query,
            (
                observation.listing_id,
                observation.pipeline_run_id,
                observation.current_price,
                observation.original_price,
                observation.shipping_cost,
                observation.currency,
                observation.available,
                observation.stock_status,
                observation.raw_price_text,
                observation.observed_at,
            ),
        )

        created_observation = self._row_to_observation(row)

        if created_observation is None:
            raise RuntimeError(
                "Price observation creation returned no data."
            )

        return created_observation

    def get_by_listing(
        self,
        listing_id: int,
        limit: int | None = None,
    ) -> list[PriceObservation]:
        """Return the historical observations of one listing."""

        query = """
            SELECT *
            FROM price_history
            WHERE listing_id = %s
            ORDER BY observed_at DESC
        """

        parameters: tuple[Any, ...]

        if limit is not None:
            query += " LIMIT %s"
            parameters = (listing_id, limit)
        else:
            parameters = (listing_id,)

        query += ";"

        rows = self.fetch_all(query, parameters)

        return [
            observation
            for row in rows
            if (
                observation := self._row_to_observation(row)
            ) is not None
        ]

    def get_latest(
        self,
        listing_id: int,
    ) -> PriceObservation | None:
        """Return the latest observation for a listing."""

        query = """
            SELECT *
            FROM price_history
            WHERE listing_id = %s
            ORDER BY observed_at DESC
            LIMIT 1;
        """

        return self._row_to_observation(
            self.fetch_one(query, (listing_id,))
        )
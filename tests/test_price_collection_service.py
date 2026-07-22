"""Unit tests for PriceCollectionService."""

import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

from src.collectors.exceptions import SourceReadError
from src.collectors.models import CollectedProductData
from src.models import (
    PipelineRun,
    PriceObservation,
    ProductListing,
    Store,
)
from src.services.exceptions import ListingNotFoundError
from src.services.price_collection_service import (
    PriceCollectionService,
)


class PriceCollectionServiceTestCase(unittest.TestCase):
    """Validate ETL service coordination."""

    def setUp(self) -> None:
        """Create mocked service dependencies."""

        self.collector = MagicMock()
        self.listing_repository = MagicMock()
        self.store_repository = MagicMock()
        self.pipeline_repository = MagicMock()
        self.price_repository = MagicMock()

        self.pipeline_repository.start.return_value = (
            PipelineRun(
                id=10,
                execution_source="test",
                status="running",
            )
        )

        self.store_repository.get_by_domain.return_value = (
            Store(
                id=20,
                name="Test Store",
                domain="test-store.local",
            )
        )

        self.listing_repository.get_by_external_id.return_value = (
            ProductListing(
                id=30,
                product_id=1,
                store_id=20,
                external_listing_id="TEST-001",
                title="Test Product",
                url="local://test-product",
            )
        )

        self.collector.collect.return_value = (
            CollectedProductData(
                external_listing_id="TEST-001",
                title="Test Product",
                current_price=Decimal("999.99"),
                original_price=Decimal("1099.99"),
                shipping_cost=Decimal("0.00"),
                currency="MXN",
                available=True,
                stock_status="Disponible",
                raw_price_text="$999.99",
            )
        )

        self.price_repository.create.return_value = (
            PriceObservation(
                id=40,
                listing_id=30,
                pipeline_run_id=10,
                current_price=Decimal("999.99"),
                currency="MXN",
                available=True,
                observed_at=datetime.now().astimezone(),
            )
        )

        self.listing_repository.update_last_seen.return_value = (
            True
        )

        self.pipeline_repository.finish.return_value = (
            PipelineRun(
                id=10,
                execution_source="test",
                status="success",
                listings_processed=1,
                successful_records=1,
                failed_records=0,
            )
        )

        self.service = PriceCollectionService(
            collector=self.collector,
            store_domain="test-store.local",
            listing_repository=(
                self.listing_repository
            ),
            store_repository=self.store_repository,
            pipeline_repository=(
                self.pipeline_repository
            ),
            price_repository=self.price_repository,
        )

    def test_successful_pipeline_execution(self) -> None:
        """A valid collection must produce a result."""

        result = self.service.execute(
            execution_source="test"
        )

        self.assertEqual(result.pipeline_run_id, 10)
        self.assertEqual(result.listing_id, 30)
        self.assertEqual(result.observation_id, 40)

        self.assertEqual(
            result.current_price,
            Decimal("999.99"),
        )

        self.pipeline_repository.start.assert_called_once_with(
            execution_source="test"
        )

        self.store_repository.get_by_domain.assert_called_once_with(
            "test-store.local"
        )

        self.listing_repository.get_by_external_id.assert_called_once_with(
            store_id=20,
            external_listing_id="TEST-001",
        )

        self.price_repository.create.assert_called_once()

        self.listing_repository.update_last_seen.assert_called_once_with(
            30
        )

        self.pipeline_repository.finish.assert_called_once_with(
            pipeline_run_id=10,
            status="success",
            listings_processed=1,
            successful_records=1,
            failed_records=0,
        )

    def test_missing_listing_marks_pipeline_failed(
        self,
    ) -> None:
        """A missing listing must create a failed run."""

        self.listing_repository.get_by_external_id.return_value = (
            None
        )

        self.pipeline_repository.finish.return_value = (
            PipelineRun(
                id=10,
                execution_source="test",
                status="failed",
                listings_processed=1,
                successful_records=0,
                failed_records=1,
            )
        )

        with self.assertRaises(ListingNotFoundError):
            self.service.execute(
                execution_source="test"
            )

        finish_call = (
            self.pipeline_repository.finish.call_args
        )

        self.assertEqual(
            finish_call.kwargs["status"],
            "failed",
        )

        self.assertEqual(
            finish_call.kwargs["failed_records"],
            1,
        )

    def test_collection_error_marks_pipeline_failed(
        self,
    ) -> None:
        """Collector failures must be persisted as failed runs."""

        self.collector.collect.side_effect = (
            SourceReadError("Source unavailable.")
        )

        self.pipeline_repository.finish.return_value = (
            PipelineRun(
                id=10,
                execution_source="test",
                status="failed",
                listings_processed=1,
                successful_records=0,
                failed_records=1,
            )
        )

        with self.assertRaises(SourceReadError):
            self.service.execute(
                execution_source="test"
            )

        finish_call = (
            self.pipeline_repository.finish.call_args
        )

        self.assertEqual(
            finish_call.kwargs["status"],
            "failed",
        )

        self.assertIn(
            "SourceReadError",
            finish_call.kwargs["error_message"],
        )


if __name__ == "__main__":
    unittest.main()
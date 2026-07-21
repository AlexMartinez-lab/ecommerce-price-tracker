"""Service coordinating product collection and persistence."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.collectors.base import ProductCollector
from src.collectors.exceptions import CollectionError
from src.models.price_observation import PriceObservation
from src.repositories.listing_repository import ListingRepository
from src.repositories.pipeline_repository import PipelineRepository
from src.repositories.price_history_repository import (
    PriceHistoryRepository,
)
from src.repositories.store_repository import StoreRepository
from src.services.exceptions import (
    ListingNotFoundError,
    PipelineExecutionError,
)


@dataclass(frozen=True, slots=True)
class PriceCollectionResult:
    """Represent the result of one successful collection."""

    pipeline_run_id: int
    listing_id: int
    observation_id: int
    product_title: str
    current_price: Decimal
    currency: str
    observed_at: datetime


class PriceCollectionService:
    """Coordinate collection, transformation and persistence."""

    def __init__(
        self,
        collector: ProductCollector,
        store_domain: str,
        listing_repository: ListingRepository | None = None,
        store_repository: StoreRepository | None = None,
        pipeline_repository: PipelineRepository | None = None,
        price_repository: PriceHistoryRepository | None = None,
    ) -> None:
        """
        Initialize the collection service.

        Args:
            collector:
                Source-specific product collector.

            store_domain:
                Domain identifying the source store.

            listing_repository:
                Optional listing repository dependency.

            store_repository:
                Optional store repository dependency.

            pipeline_repository:
                Optional pipeline repository dependency.

            price_repository:
                Optional price history repository dependency.
        """

        self.collector = collector
        self.store_domain = store_domain

        self.listing_repository = (
            listing_repository or ListingRepository()
        )

        self.store_repository = (
            store_repository or StoreRepository()
        )

        self.pipeline_repository = (
            pipeline_repository or PipelineRepository()
        )

        self.price_repository = (
            price_repository or PriceHistoryRepository()
        )

    def execute(
        self,
        execution_source: str = "manual",
    ) -> PriceCollectionResult:
        """
        Execute one complete product collection pipeline.

        The service:

        1. Registers the pipeline execution.
        2. Collects normalized product data.
        3. Finds the registered store and listing.
        4. Creates an immutable price observation.
        5. Updates the listing's last-seen timestamp.
        6. Marks the pipeline run as successful.

        Args:
            execution_source:
                Origin of the execution, such as manual or cron.

        Returns:
            Information about the successful pipeline execution.

        Raises:
            ListingNotFoundError:
                If the store or listing is not registered.

            PipelineExecutionError:
                If collection or persistence fails.
        """

        pipeline_run = self.pipeline_repository.start(
            execution_source=execution_source
        )

        if pipeline_run.id is None:
            raise PipelineExecutionError(
                "The pipeline run was created without an ID."
            )

        pipeline_run_id = pipeline_run.id

        try:
            collected_data = self.collector.collect()

            store = self.store_repository.get_by_domain(
                self.store_domain
            )

            if store is None or store.id is None:
                raise ListingNotFoundError(
                    "No registered store was found for domain: "
                    f"{self.store_domain}"
                )

            listing = (
                self.listing_repository.get_by_external_id(
                    store_id=store.id,
                    external_listing_id=(
                        collected_data.external_listing_id
                    ),
                )
            )

            if listing is None or listing.id is None:
                raise ListingNotFoundError(
                    "No registered listing was found for "
                    f"{collected_data.external_listing_id!r} "
                    f"in store {self.store_domain!r}."
                )

            observed_at = datetime.now().astimezone()

            observation = self.price_repository.create(
                PriceObservation(
                    listing_id=listing.id,
                    pipeline_run_id=pipeline_run_id,
                    current_price=(
                        collected_data.current_price
                    ),
                    original_price=(
                        collected_data.original_price
                    ),
                    shipping_cost=(
                        collected_data.shipping_cost
                    ),
                    currency=collected_data.currency,
                    available=collected_data.available,
                    stock_status=(
                        collected_data.stock_status
                    ),
                    raw_price_text=(
                        collected_data.raw_price_text
                    ),
                    observed_at=observed_at,
                )
            )

            if observation.id is None:
                raise PipelineExecutionError(
                    "The price observation was created "
                    "without an ID."
                )

            updated = (
                self.listing_repository.update_last_seen(
                    listing.id
                )
            )

            if not updated:
                raise PipelineExecutionError(
                    "The listing last-seen timestamp "
                    "could not be updated."
                )

            finished_run = self.pipeline_repository.finish(
                pipeline_run_id=pipeline_run_id,
                status="success",
                listings_processed=1,
                successful_records=1,
                failed_records=0,
            )

            if finished_run.status != "success":
                raise PipelineExecutionError(
                    "The pipeline execution did not finish "
                    "with success status."
                )

            return PriceCollectionResult(
                pipeline_run_id=pipeline_run_id,
                listing_id=listing.id,
                observation_id=observation.id,
                product_title=collected_data.title,
                current_price=observation.current_price,
                currency=observation.currency,
                observed_at=observation.observed_at,
            )

        except Exception as error:
            self._mark_pipeline_as_failed(
                pipeline_run_id=pipeline_run_id,
                error=error,
            )

            if isinstance(
                error,
                (
                    CollectionError,
                    ListingNotFoundError,
                    PipelineExecutionError,
                ),
            ):
                raise

            raise PipelineExecutionError(
                "Unexpected pipeline execution failure."
            ) from error

    def _mark_pipeline_as_failed(
        self,
        pipeline_run_id: int,
        error: Exception,
    ) -> None:
        """Record a failed pipeline execution."""

        error_message = (
            f"{type(error).__name__}: {error}"
        )

        try:
            self.pipeline_repository.finish(
                pipeline_run_id=pipeline_run_id,
                status="failed",
                listings_processed=1,
                successful_records=0,
                failed_records=1,
                error_message=error_message[:2000],
            )

        except Exception:
            # The original exception is more important.
            # Logging will be added in a later stage.
            pass
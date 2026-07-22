"""Execute the controlled end-to-end ETL pipeline."""

import sys
from pathlib import Path

from src.collectors import LocalHtmlCollector
from src.collectors.exceptions import CollectionError
from src.services.exceptions import (
    ListingNotFoundError,
    PipelineExecutionError,
)
from src.services.price_collection_service import (
    PriceCollectionService,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

HTML_FIXTURE = (
    PROJECT_ROOT
    / "data"
    / "fixtures"
    / "sample_product.html"
)

CONTROLLED_STORE_DOMAIN = "demo-store.local"


def main() -> None:
    """Run and display one controlled pipeline execution."""

    collector = LocalHtmlCollector(HTML_FIXTURE)

    service = PriceCollectionService(
        collector=collector,
        store_domain=CONTROLLED_STORE_DOMAIN,
    )

    try:
        result = service.execute(
            execution_source="manual"
        )

    except (
        CollectionError,
        ListingNotFoundError,
        PipelineExecutionError,
    ) as error:
        print("Controlled ETL pipeline failed.")
        print(
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)

    print("Controlled ETL pipeline completed.")
    print("-" * 60)
    print(f"Pipeline run ID: {result.pipeline_run_id}")
    print(f"Listing ID: {result.listing_id}")
    print(
        f"Observation ID: {result.observation_id}"
    )
    print(f"Product: {result.product_title}")
    print(
        f"Recorded price: "
        f"${result.current_price:,.2f} "
        f"{result.currency}"
    )
    print(f"Observed at: {result.observed_at}")


if __name__ == "__main__":
    main()
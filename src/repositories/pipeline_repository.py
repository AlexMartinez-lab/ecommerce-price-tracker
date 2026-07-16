"""Data access operations for pipeline executions."""

from typing import Any

from src.models.pipeline_run import PipelineRun
from src.repositories.base_repository import BaseRepository


class PipelineRepository(BaseRepository):
    """Manage ETL pipeline execution records."""

    @staticmethod
    def _row_to_pipeline_run(
        row: dict[str, Any] | None,
    ) -> PipelineRun | None:
        """Convert a database row into a PipelineRun object."""

        if row is None:
            return None

        return PipelineRun(
            id=row["id"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            status=row["status"],
            listings_processed=row["listings_processed"],
            successful_records=row["successful_records"],
            failed_records=row["failed_records"],
            error_message=row["error_message"],
            execution_source=row["execution_source"],
            created_at=row["created_at"],
        )

    def start(self, execution_source: str = "manual") -> PipelineRun:
        """Register the beginning of one pipeline execution."""

        query = """
            INSERT INTO pipeline_runs (
                execution_source,
                status
            )
            VALUES (%s, 'running')
            RETURNING *;
        """

        row = self.fetch_one(query, (execution_source,))
        pipeline_run = self._row_to_pipeline_run(row)

        if pipeline_run is None:
            raise RuntimeError(
                "Pipeline execution creation returned no data."
            )

        return pipeline_run

    def finish(
        self,
        pipeline_run_id: int,
        status: str,
        listings_processed: int,
        successful_records: int,
        failed_records: int,
        error_message: str | None = None,
    ) -> PipelineRun:
        """Complete one pipeline execution."""

        query = """
            UPDATE pipeline_runs
            SET
                finished_at = CURRENT_TIMESTAMP,
                status = %s,
                listings_processed = %s,
                successful_records = %s,
                failed_records = %s,
                error_message = %s
            WHERE id = %s
            RETURNING *;
        """

        row = self.fetch_one(
            query,
            (
                status,
                listings_processed,
                successful_records,
                failed_records,
                error_message,
                pipeline_run_id,
            ),
        )

        pipeline_run = self._row_to_pipeline_run(row)

        if pipeline_run is None:
            raise LookupError(
                f"Pipeline run {pipeline_run_id} was not found."
            )

        return pipeline_run

    def get_by_id(
        self,
        pipeline_run_id: int,
    ) -> PipelineRun | None:
        """Return a pipeline execution by ID."""

        query = """
            SELECT *
            FROM pipeline_runs
            WHERE id = %s;
        """

        return self._row_to_pipeline_run(
            self.fetch_one(query, (pipeline_run_id,))
        )

    def get_recent(self, limit: int = 20) -> list[PipelineRun]:
        """Return the most recent pipeline executions."""

        query = """
            SELECT *
            FROM pipeline_runs
            ORDER BY started_at DESC
            LIMIT %s;
        """

        rows = self.fetch_all(query, (limit,))

        return [
            run
            for row in rows
            if (run := self._row_to_pipeline_run(row)) is not None
        ]
"""Pipeline execution domain model."""


from dataclasses import dataclass
from datetime import datetime



@dataclass(slots=True)
class PipelineRun:
	"""Represent one ETL pipeline execution."""


	execution_source: str = "manual"
	status: str = "running"
	listings_processed: int = 0
	successful_records: int = 0
	failed_records: int = 0
	error_message: str | None = None
	id: int | None = None
	started_at: datetime | None = None
	finished_at: datetime | None = None
	created_at: datetime | None = None

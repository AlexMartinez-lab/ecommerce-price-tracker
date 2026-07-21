"""Exceptions raised by application services."""


class ServiceError(Exception):
    """Base exception for application service failures."""


class ListingNotFoundError(ServiceError):
    """Raised when a collected listing is not registered."""


class PipelineExecutionError(ServiceError):
    """Raised when a collection pipeline cannot be completed."""
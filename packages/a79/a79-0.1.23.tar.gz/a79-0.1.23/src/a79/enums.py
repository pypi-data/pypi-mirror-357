from enum import Enum


class RunStatus(str, Enum):
    # NOTE: When new statuses are added, alembic does not pick up the new enum
    # values. So, we need to create an alembic migration to include the
    # new statuses.
    UNDEFINED = "undefined"
    NOT_STARTED = "not_started"
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    SUCCEEDED = "succeeded"
    PARTIAL_SUCCESS = "partial_success"
    SKIPPED = "skipped"
    PAUSED = "paused"
    CANCELLED = "cancelled"

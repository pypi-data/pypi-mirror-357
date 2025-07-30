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


class CustomDataType(str, Enum):
    TEXT = "text"
    BOOL = "bool"
    EMAIL = "email"
    DATETIME = "datetime"
    TIME = "time"
    DATE = "date"
    NUMBER = "number"
    DOCUMENT = "document"
    FOLDER = "folder"
    INPUT_TEMPLATE = "input_template"
    URL = "url"
    EXCEL = "excel"
    ENUM = "enum"


class ModelName(str, Enum):
    """
    Enum class for standardized model names used across the codebase.
    """

    GEMINI_FLASH = "gemini/gemini-2.5-flash-preview-05-20"
    GEMINI_PRO = "gemini/gemini-2.5-pro-preview-05-06"
    GPT_4O = "gpt-4o"
    CLAUDE_SONNET = "claude-3-5-sonnet-20240620"
    GPT_4O_MINI = "gpt-4o-mini"
    GEMINI_FLASH_1_5 = "gemini/gemini-1.5-flash"
    O4_MINI = "o4-mini"
    O3 = "o3"

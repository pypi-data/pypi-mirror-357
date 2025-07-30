import os
from dataclasses import dataclass
from enum import Enum


class StatusCode(Enum):
    """
    Enum class for various status codes.
    """

    OK = 0
    ERROR = 1


class DSLStepOperationType(str, Enum):
    """Type of operation for a DSL step"""

    CREATE = "CREATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    ADD = "ADD"


class DataSourceStatus(str, Enum):
    PENDING = "pending"
    PROCESSING_FAILED = "processing_failed"
    PROCESSING_SUCCEEDED = "processing_succeeded"


class DataSourceType(str, Enum):
    USER_UPLOADED = "user_uploaded"
    WORKSHEET = "worksheet"
    CONNECTOR_GENERATED = "connector_generated"


class ColumnEnrichmentStatus(str, Enum):
    ENRICHMENT_COMPLETE = "enrichment_complete"
    ENRICHMENT_IN_PROGRESS = "enrichment_in_progress"
    ENRICHMENT_FAILED = "enrichment_failed"
    INDEXING_COMPLETE = "indexing_complete"
    INDEXING_IN_PROGRESS = "indexing_in_progress"
    INDEXING_FAILED = "indexing_failed"


class ActionType(str, Enum):
    NO_ACTION = "NO_ACTION"
    WORKFLOW_GEN_NL_TO_DSL = "WORKFLOW_GEN_NL_TO_DSL"
    WORKFLOW_GEN_DSL_TO_CODE = "WORKFLOW_GEN_DSL_TO_CODE"
    WORKFLOW_GEN_NL_TO_YAML = "WORKFLOW_GEN_NL_TO_YAML"
    WORKFLOW_GEN_NL_TO_DSL_AND_YAML_ADD_MODE = "WORKFLOW_GEN_NL_TO_DSL_AND_YAML_ADD_MODE"
    WORKFLOW_REACT_IMPROVE = "WORKFLOW_REACT_IMPROVE"
    WORKFLOW_GEN_NL_TO_RESULT_WITH_REACT = "WORKFLOW_GEN_NL_TO_RESULT_WITH_REACT"


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


class OutputPresentationType(str, Enum):
    HEADING_BULLET = 1
    HEADING_PARA = 2
    DUAL_HEADING = 3
    HEADING_SUBHEADING = 4


class FunctionType(str, Enum):
    SYNC_ACTION = "sync_action"
    LLM = "llm"
    FORMULA = "formula"


class ReportTemplateType(str, Enum):
    OUTPUT_DOCX = "output_docx"
    PROMPT = "prompt"
    OUTPUT_SLIDE = "output_slide"


class UserRole(str, Enum):
    UNASSIGNED = "unassigned"
    USER = "user"
    ADMIN = "admin"


class UserInviteConnectionType(str, Enum):
    GOOGLE_OAUTH = "google-oauth"
    USERNAME_PASSWORD = "username-password"
    OKTA = "okta"


class BlockType(str, Enum):
    """
    Enum class for various block types.
    """

    INLINE_PROMPT = "inline_prompt"
    CHART = "chart"
    GRAPH = "graph"
    CONVERSATION = "conversation"


class SearchResultSource(str, Enum):
    SEMANTIC = "semantic"
    LEXICAL = "lexical"
    HYBRID = "hybrid"


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ACTION = "action"


class PresentationType(str, Enum):
    SLIDES = "slides"
    DOCX = "docx"


class CallStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT_FAILED = "timeout_failed"


@dataclass(frozen=True)
class ContentTypeInfo:
    mime_type: str
    extensions: list[str]


class ContentType(Enum):
    DOC = ContentTypeInfo(mime_type="application/msword", extensions=["doc"])
    DOCX = ContentTypeInfo(
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        extensions=["docx"],
    )
    CSV = ContentTypeInfo(mime_type="text/csv", extensions=["csv"])
    PDF = ContentTypeInfo(mime_type="application/pdf", extensions=["pdf"])
    PPTX = ContentTypeInfo(
        mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        extensions=["pptx"],
    )
    XLSX = ContentTypeInfo(
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        extensions=["xlsx", "xlsm"],
    )
    PPT = ContentTypeInfo(mime_type="application/vnd.ms-powerpoint", extensions=["ppt"])
    HTML = ContentTypeInfo(mime_type="text/html", extensions=["html", "htm"])
    PLAIN_TEXT = ContentTypeInfo(
        mime_type="text/plain", extensions=["md", "markdown", "txt", "text"]
    )
    PNG = ContentTypeInfo(mime_type="image/png", extensions=["png"])
    JPEG = ContentTypeInfo(mime_type="image/jpeg", extensions=["jpg", "jpeg"])
    MP3 = ContentTypeInfo(mime_type="audio/mpeg", extensions=["mp3"])
    MPGA = ContentTypeInfo(mime_type="audio/mpeg", extensions=["mpga"])
    WAV = ContentTypeInfo(mime_type="audio/wav", extensions=["wav"])
    M4A = ContentTypeInfo(mime_type="audio/mp4", extensions=["m4a"])
    OGG = ContentTypeInfo(mime_type="audio/ogg", extensions=["ogg"])
    MPEG = ContentTypeInfo(mime_type="video/mpeg", extensions=["mpeg", "mpg"])
    MP4 = ContentTypeInfo(mime_type="video/mp4", extensions=["mp4"])
    WEBM = ContentTypeInfo(mime_type="video/webm", extensions=["webm"])
    ZIP = ContentTypeInfo(mime_type="application/zip", extensions=["zip"])
    DEFAULT_UPLOAD_TYPE = ContentTypeInfo(
        mime_type="application/octet-stream", extensions=[]
    )
    EML = ContentTypeInfo(mime_type="message/rfc822", extensions=["eml"])

    @classmethod
    def get_all_supported_extensions(cls) -> set[str]:
        """Returns a set of all supported file extensions."""
        extensions = set()
        for content_type in cls:
            extensions.update(content_type.value.extensions)
        return extensions

    @classmethod
    def get_all_mime_types(cls) -> set[str]:
        """Returns a set of all supported file extensions."""
        extensions = set()
        for content_type in cls:
            extensions.add(content_type.value.mime_type)
        return extensions

    @classmethod
    def from_filepath(cls, filepath: str) -> "ContentType":
        _, extension = os.path.splitext(filepath)
        return cls.from_extension(extension)

    @classmethod
    def from_extension(cls, extension: str) -> "ContentType":
        """
        Get ContentType from file extension.
        Raises ValueError if extension is not supported.
        """
        extension = extension.lower().lstrip(".")
        for content_type in cls:
            if extension in content_type.value.extensions:
                return content_type
        raise ValueError(f"Unsupported file extension: {extension}")

    @classmethod
    def from_mime_type(cls, mime_type: str) -> "ContentType":
        """
        Get ContentType from MIME type.
        Raises ValueError if MIME type is not supported.
        """
        for content_type in cls:
            if content_type.value.mime_type == mime_type:
                return content_type
        raise ValueError(f"Unsupported MIME type: {mime_type}")


# TODO(Ajeet): ConnectorType may refer to a tap, or a special-cased connector that doesn't
# store any data. This is causing complexity in a bunch of places - eventually, we should
# change this enum to TapType, and move out anything that is not a Singer connector.
class ConnectorType(str, Enum):
    # BOX = "box"
    DROPBOX = "dropbox"
    DYNAMODB = "dynamodb"
    GITHUB = "github"
    GMAIL = "gmail"
    GOOGLEDRIVE = "googledrive"
    JIRA = "jira"
    LINKEDIN = "linkedin"
    MASTERCONTROL = "mastercontrol"
    # Mock connector is for testing purposes only.
    MOCK = "mock"
    MONDAY = "monday"
    POSTGRES_URL = "postgres_url"
    PROQUEST = "proquest"
    PUBMED = "pubmed"
    SERVICENOW = "servicenow"
    SHAREPOINT = "sharepoint"
    # Starburst API based connector for getting their custom data documentation details.
    STARBURST_API = "starburst_api"
    STARBURST_ENTERPRISE = "starburst_enterprise"
    # Trino is the underlying datastore that Starburst exposes.
    TRINO = "trino"


class ConnectorStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"


class TargetType(str, Enum):
    """
    TargetType specifies where the data generated by a connector is stored.
    """

    WORKSHEET = "worksheet"
    """Stores all generated data in a worksheet."""

    NONE = "none"
    """
    Some of the connectors we use have been implemented in a way that is not
    Singer-compliant (i.e., they don't use taps and targets). For such connectors, we
    mark them as TargetType.NONE till they are properly implemented.
    """


class EnrichmentActionEnum(str, Enum):
    """
    These are enums representing pre-defined actions that can be performed in an
    enrichment function. It basically encapsulates,

    result: List[Result] = Function(enrichment-action, dataframe)

    This is quite similar to how LLM or Formula functions work, but differ in who
    owns the action enumeration. For LLM and Formula functions, enrichment_function
    owns the implementation. With ActionEnums, different parts of the stack can
    define their own actions and register it. This enables enrichment_function as an
    abstraction to not leak everywhere and be aware of different action implementations.
    """

    CREATE_DATASOURCE = "create_datasource"

    EXTRACT_RAW_TRANSCRIPT = "extract_raw_transcript"

    CREATE_COLUMN_FROM_JSON_FIELD = "create_column_from_json_field"

    DETECT_SILENCE_IN_AUDIO = "detect_silence_in_audio"

    DETECT_NOISE_IN_AUDIO = "detect_noise_in_audio"

    DETECT_EMOTION_IN_AUDIO = "detect_emotion_in_audio"

    ANALYZE_CALL_TRANSCRIPT = "analyze_call_transcript"

    GENERATE_CALL_CRITIQUE = "generate_call_critique"

    # Add more actions as needed


class InputTemplateType(str, Enum):
    QUESTIONS = "questions"


class UserActionType(str, Enum):
    """
    Enum class for user action type. This is used to represent the type of user action
    that is provided on the workflow node.
    """

    NONE = "none"
    APPROVED = "approved"
    CANCELLED = "cancelled"
    EDITED = "edited"


class WorkflowGenAttemptStage(str, Enum):
    UNDEFINED = "undefined"
    NL_TO_DSL = "nl_to_dsl"
    DSL_TO_CODE = "dsl_to_code"
    YAML_VALIDATION = "yaml_validation"
    WORKFLOW_EXECUTION = "workflow_execution"


class TextEditCommandType(str, Enum):
    """
    Enum class for text editing command types used in text feedback functionality.
    """

    IMPROVE = "improve"
    FIX_SPELLING = "fix-spelling"
    MAKE_SHORTER = "make-shorter"
    MAKE_LONGER = "make-longer"
    SIMPLIFY = "simplify"
    TRANSLATE = "translate"
    SUMMARIZE = "summarize"
    CONTINUE = "continue"
    CUSTOM = "custom"


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


class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    NOT_FOUND = "not_found"

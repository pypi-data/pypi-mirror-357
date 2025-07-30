"""Definition of Delos endpoints and their request types."""

from enum import Enum


class RequestMethod(str, Enum):
    """Enum representing the type of HTTP requests."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class StatusEndpoints(Enum):
    """Enum containing the status service endpoints and their request types."""

    HEALTH = ("/health", RequestMethod.GET)


class TranslateEndpoints(Enum):
    """Enum containing the translate service endpoints and their request types."""

    TRANSLATE_TEXT = ("/translate-text", RequestMethod.POST)
    TRANSLATE_FILE = ("/translate-file", RequestMethod.POST)


class WebEndpoints(Enum):
    """Enum containing the web service endpoints and their request types."""

    SEARCH = ("/search", RequestMethod.POST)


class FileEndpoints(Enum):
    """Enum containing the file service endpoints and their request types."""

    INDEX_CREATE = ("/files/create_index_and_parse", RequestMethod.POST)
    INDEX_ADD_FILES = ("/files/add_files_to_index", RequestMethod.POST)
    INDEX_RETRY_FILES = ("/files/retry_failed_files", RequestMethod.PUT)
    INDEX_RESTORE = ("/files/restore_index", RequestMethod.PUT)
    INDEX_RENAME = ("/files/rename_index", RequestMethod.PUT)
    INDEX_DELETE_FILES = ("/files/delete_files_from_index", RequestMethod.DELETE)
    INDEX_DELETE = ("/files/delete_index", RequestMethod.DELETE)

    INDEX_ASK = ("/files/ask_index", RequestMethod.POST)
    INDEX_EMBED = ("/files/embed_index", RequestMethod.POST)
    INDEX_LIST = ("/files/list_index", RequestMethod.GET)
    INDEX_DETAILS = ("/files/index_details", RequestMethod.GET)


class FileTagsEndpoints(Enum):
    """Enum containing the file tags service endpoints and their request types."""

    INDEX_GET_TAGS = ("/files/get_index_tags", RequestMethod.GET)
    INDEX_UPDATE_TAGS = ("/files/update_index_tags", RequestMethod.PUT)
    INDEX_UPDATE_FILE_TAGS = ("/files/update_index_files_tags", RequestMethod.PUT)


class LlmEndpoints(Enum):
    """Enum containing the LLM service endpoints and their request types."""

    CHAT = ("/llm/chat", RequestMethod.POST)
    CHAT_STREAM = ("/llm/chat_stream", RequestMethod.POST)
    CHAT_BETA = ("/llm/chat/beta", RequestMethod.POST)
    EMBED = ("/llm/embed", RequestMethod.POST)


class Endpoints:
    """Class grouping all the different types of endpoints."""

    STATUS = StatusEndpoints
    WEB = WebEndpoints
    TRANSLATE = TranslateEndpoints
    FILES = FileEndpoints
    FILES_TAGS = FileTagsEndpoints
    LLM = LlmEndpoints


DelosEndpoints = StatusEndpoints | WebEndpoints | TranslateEndpoints | FileEndpoints | FileTagsEndpoints | LlmEndpoints

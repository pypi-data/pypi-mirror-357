"""inference.sh Python SDK package."""

__version__ = "0.1.2"

from .models import (
    BaseApp,
    BaseAppInput,
    BaseAppOutput,
    File,
    ContextMessageRole,
    Message,
    ContextMessage,
    ContextMessageWithImage,
    LLMInput,
    LLMInputWithImage,
)
from .utils import StorageDir, download

__all__ = [
    "BaseApp",
    "BaseAppInput",
    "BaseAppOutput",
    "File",
    "ContextMessageRole",
    "Message",
    "ContextMessage",
    "ContextMessageWithImage",
    "LLMInput",
    "LLMInputWithImage",
    "StorageDir",
    "download",
]
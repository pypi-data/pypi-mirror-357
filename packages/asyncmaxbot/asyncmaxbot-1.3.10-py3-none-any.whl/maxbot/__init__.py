"""
Max Bot API Client - Python библиотека для работы с Max API
"""

from .bot import Bot
from .dispatcher import Dispatcher
from .filters import Command, Text, Regex, Attachment, attachment_type, has_attachment
from .max_types import (
    Context,
    Update,
    Message,
    MessageBody,
    User,
    Chat,
    BaseAttachment
)
from .middleware import MiddlewareManager, LoggingMiddleware, ErrorHandlingMiddleware

__version__ = "0.1.0"
__author__ = "Max Bot API Client Team"

__all__ = [
    "Bot",
    "Dispatcher",
    "Context",
    "Update",
    "Message",
    "MessageBody",
    "User",
    "Chat",
    "Command",
    "Text",
    "Regex",
    "Attachment",
    "attachment_type",
    "has_attachment",
    "BaseAttachment",
    "MiddlewareManager",
    "LoggingMiddleware",
    "ErrorHandlingMiddleware",
] 
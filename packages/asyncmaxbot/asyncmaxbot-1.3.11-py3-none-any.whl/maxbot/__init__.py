"""
AsyncMaxBot - Python library for creating bots in Max API with aiogram-like syntax
"""

__version__ = "1.3.11"

from .bot import Bot
from .dispatcher import Dispatcher
from .max_types import *
from .filters import F
from .middleware import BaseMiddleware

__all__ = [
    "Bot",
    "Dispatcher", 
    "F",
    "BaseMiddleware",
    # Types
    "User",
    "Chat",
    "Message",
    "CallbackQuery",
    "InlineKeyboardMarkup",
    "InlineKeyboardButton",
    "BaseAttachment",
    "ImageAttachment",
    "VideoAttachment", 
    "AudioAttachment",
    "FileAttachment",
    "StickerAttachment",
    "LocationAttachment",
    "ShareAttachment",
] 
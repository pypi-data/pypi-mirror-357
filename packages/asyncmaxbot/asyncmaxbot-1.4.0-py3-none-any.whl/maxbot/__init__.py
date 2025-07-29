"""
AsyncMaxBot SDK - Асинхронная библиотека для создания ботов в MaxAPI

Основные компоненты:
- Bot: Основной класс для работы с MaxAPI
- Dispatcher: Диспетчер для обработки обновлений
- Context: Контекст обработки сообщений
- Router: Система роутеров для модульной архитектуры
- Filters: Система фильтров для обработчиков
- Middleware: Система промежуточного ПО

Пример использования:
    from maxbot import Bot, Dispatcher
    
    bot = Bot("YOUR_TOKEN")
    dp = Dispatcher(bot)
    
    @dp.message_handler()
    async def handle_message(ctx):
        await ctx.reply("Привет!")
    
    async def main():
        async with bot:
            await bot.polling(dispatcher=dp)
"""

__version__ = "1.4.0"
__author__ = "SDK Infotech"
__email__ = "info@sdkinfotech.com"

from .bot import Bot
from .dispatcher import Dispatcher
from .max_types import (
    Context,
    Update,
    Message,
    User,
    Chat,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BaseAttachment,
    ImageAttachment,
    VideoAttachment,
    AudioAttachment,
    FileAttachment,
    StickerAttachment,
    LocationAttachment,
    ShareAttachment,
    BotStarted,
    UserAdded,
    ChatMemberUpdated,
)
from .filters import F
from .middleware import Middleware, MiddlewareManager
from .router import Router

__all__ = [
    # Основные классы
    "Bot",
    "Dispatcher",
    "Context",
    "Router",
    
    # Типы данных
    "Update",
    "Message",
    "User",
    "Chat",
    "CallbackQuery",
    
    # Клавиатуры
    "InlineKeyboardMarkup",
    "InlineKeyboardButton",
    
    # Вложения
    "BaseAttachment",
    "ImageAttachment",
    "VideoAttachment",
    "AudioAttachment",
    "FileAttachment",
    "StickerAttachment",
    "LocationAttachment",
    "ShareAttachment",
    
    # Расширенные события
    "BotStarted",
    "UserAdded",
    "ChatMemberUpdated",
    
    # Фильтры и middleware
    "F",
    "Middleware",
    "MiddlewareManager",
] 
"""
Диспетчер для обработки обновлений MaxBot
"""

import asyncio
from typing import Callable, List, Optional, Union, TYPE_CHECKING
from loguru import logger

if TYPE_CHECKING:
    from .bot import Bot

from .max_types import Context, Update
from .filters import BaseFilter
from .middleware import MiddlewareManager

class Handler:
    """
    Контейнер для хранения обработчика (callback) и связанных с ним фильтров.
    """
    
    def __init__(self, callback: Callable, filters: Optional[List[BaseFilter]] = None):
        """
        :param callback: Функция-обработчик, которая будет вызвана.
        :param filters: Список фильтров, которые должны быть пройдены.
        """
        self.callback = callback
        self.filters = filters or []
    
    async def check(self, ctx: Context) -> bool:
        """
        Проверяет, соответствует ли контекст всем фильтрам этого обработчика.

        :param ctx: Объект Context для проверки.
        :return: True, если все фильтры пройдены, иначе False.
        """
        for filter_obj in self.filters:
            if not await filter_obj.check(ctx):
                return False
        return True

class Dispatcher:
    """
    Диспетчер обрабатывает входящие обновления, пропускает их через Middleware,
    находит подходящий обработчик на основе фильтров и вызывает его.
    """
    
    def __init__(self, bot: 'Bot'):
        """
        :param bot: Экземпляр класса Bot.
        """
        self.bot = bot
        self.handlers: List[Handler] = []
        self.middleware_manager = MiddlewareManager()
    
    def message_handler(self, *filters: BaseFilter):
        """
        Декоратор для регистрации обработчика сообщений.

        Пример:
        @dp.message_handler(Command("start"))
        async def start_command(ctx: Context):
            await ctx.reply("Привет!")

        :param filters: Последовательность фильтров. Обработчик сработает,
                        если все фильтры вернут True.
        """
        def decorator(func: Callable):
            handler = Handler(func, list(filters))
            self.handlers.append(handler)
            return func
        return decorator
    
    def register_message_handler(self, callback: Callable, *filters: BaseFilter):
        """
        Альтернативный способ регистрации обработчика без декоратора.

        :param callback: Функция-обработчик.
        :param filters: Фильтры для обработчика.
        """
        handler = Handler(callback, list(filters))
        self.handlers.append(handler)
    
    def add_middleware(self, middleware):
        """
        Добавляет Middleware для обработки всех входящих обновлений.

        :param middleware: Объект Middleware.
        """
        self.middleware_manager.add_middleware(middleware)
    
    async def process_update(self, update_data: dict):
        """
        Основной метод обработки входящего обновления.

        Парсит сырые данные, создает Context и ищет подходящий обработчик.

        :param update_data: Словарь с данными обновления от API.
        """
        logger.debug(f"Processing update data: {update_data}")
        try:
            update = Update.model_validate(update_data)
            
            if not update.message:
                logger.warning(f"Update without message: {update}")
                return

            ctx = Context(update, self.bot)
            logger.debug(f"Created context. Text: '{ctx.text}', Attachments: {ctx.attachments}")
            
            # Ищем подходящий хендлер
            for handler in self.handlers:
                try:
                    filter_check_result = await handler.check(ctx)
                    logger.debug(f"Checking handler '{getattr(handler.callback, '__name__', 'unknown')}' -> Filter check: {filter_check_result}")
                    if filter_check_result:
                        logger.info(f"Found handler '{getattr(handler.callback, '__name__', 'unknown')}'. Processing...")
                        # Обрабатываем через middleware
                        await self.middleware_manager.process(ctx, handler.callback)
                        return # Первый подходящий хендлер
                except Exception as e:
                    logger.error(f"Error in handler '{getattr(handler.callback, '__name__', 'unknown')}': {e}", exc_info=True)
            
            logger.warning(f"No matching handler for text: '{ctx.text}'")
                    
        except Exception as e:
            logger.error(f"Error processing update: {e}", exc_info=True)
            logger.debug(f"Update data that caused error: {update_data}") 
"""
Эхо-бот - стандартная архитектура
Демонстрирует базовые возможности библиотеки
"""

import asyncio
import os
from maxbot import Bot
from maxbot.dispatcher import Dispatcher
from maxbot.filters import command, text
from maxbot.middleware import MiddlewareManager, LoggingMiddleware, ErrorHandlingMiddleware
from maxbot.max_types import Context

# Загружаем токен из файла
def get_token():
    token_file = "token.txt"
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            return f.read().strip()
    return os.environ.get("MAXBOT_TOKEN", "YOUR_TOKEN_HERE")

TOKEN = get_token()  # Загружаем из файла

class EchoBot:
    """Эхо-бот с стандартной архитектурой"""
    
    def __init__(self):
        self.bot = Bot(TOKEN)
        self.dp = Dispatcher(self.bot)
        self.setup_middleware()
        self.setup_handlers()
        self.stats = {"messages": 0, "users": set()}
    
    def setup_middleware(self):
        """Настройка базового middleware"""
        manager = MiddlewareManager()
        manager.add_middleware(LoggingMiddleware())
        manager.add_middleware(ErrorHandlingMiddleware())
        self.dp.middleware_manager = manager
    
    def setup_handlers(self):
        """Настройка обработчиков"""
        
        @self.dp.message_handler(command("start"))
        async def start_handler(ctx: Context):
            await ctx.reply(
                f"👋 Привет, {ctx.user.name}! Я эхо-бот.\n"
                "📝 Просто напиши что-нибудь, и я повторю это.\n"
                "📊 /stats — статистика\n"
                "🔄 /echo — режим эхо\n"
                "❓ /help — эта справка"
            )
        
        @self.dp.message_handler(command("help"))
        async def help_handler(ctx: Context):
            await ctx.reply(
                "📚 Справка по эхо-боту:\n\n"
                "💬 Просто напишите любое сообщение, и я его повторю\n"
                "📊 /stats — показать статистику\n"
                "🔄 /echo — включить режим эхо\n"
                "❓ /help — эта справка"
            )
        
        @self.dp.message_handler(command("stats"))
        async def stats_handler(ctx: Context):
            self.stats["messages"] += 1
            self.stats["users"].add(ctx.user_id)
            
            await ctx.reply(
                f"📊 Статистика:\n"
                f"💬 Сообщений: {self.stats['messages']}\n"
                f"👥 Уникальных пользователей: {len(self.stats['users'])}"
            )
        
        @self.dp.message_handler(command("echo"))
        async def echo_mode_handler(ctx: Context):
            await ctx.reply("🔄 Режим эхо включен! Напиши что-нибудь.")
        
        @self.dp.message_handler(text("привет", exact=False))
        async def hello_handler(ctx: Context):
            emoji = "🦜" if "привет" in ctx.text.lower() else "📢"
            await ctx.reply(f"{emoji} {ctx.text}")
        
        @self.dp.message_handler()
        async def echo_handler(ctx: Context):
            """
            Этот обработчик ловит любое сообщение и отвечает тем же текстом.
            Демонстрирует:
            - Регистрацию обработчика без фильтров (срабатывает на все).
            - Использование `ctx.text` для получения текста.
            - Использование `ctx.reply` для ответа.
            """
            self.stats["messages"] += 1
            self.stats["users"].add(ctx.user_id)
            
            if ctx.text.startswith("/"):
                await ctx.reply("❓ Неизвестная команда. Напиши /help")
            else:
                emoji = "🦜" if "привет" in ctx.text.lower() else "📢"
                await ctx.reply(f"{emoji} {ctx.text}")
    
    async def run(self):
        """Запуск бота"""
        print("🤖 Эхо-бот запущен!")
        
        async with self.bot:
            me = await self.bot.get_me()
            print(f"🤖 Бот: {me['name']} (ID: {me['user_id']})")
            
            await self.bot.polling(
                dispatcher=self.dp,
                timeout=1,
                long_polling_timeout=30
            )

async def main():
    """Основная функция для запуска бота."""
    bot = EchoBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main()) 
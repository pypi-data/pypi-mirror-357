"""
Бот-секретарь - стандартная архитектура
Демонстрирует работу с состоянием и данными
"""

import asyncio
import os
from datetime import datetime
from maxbot import Bot
from maxbot.dispatcher import Dispatcher
from maxbot.filters import command, text, has_attachment
from maxbot.middleware import MiddlewareManager, LoggingMiddleware, ErrorHandlingMiddleware
from maxbot.max_types import Context

TOKEN = "YOUR_TOKEN_HERE"  # Замените на ваш токен

class SecretaryBot:
    """Бот-секретарь с стандартной архитектурой"""
    
    def __init__(self):
        self.bot = Bot(TOKEN)
        self.dp = Dispatcher(self.bot)
        self.setup_middleware()
        self.setup_handlers()
        self.applications = []
        self.reminders = {}
    
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
                f"👋 Здравствуйте, {ctx.user.name}! Я ваш виртуальный секретарь.\n\n"
                "📋 Доступные команды:\n"
                "📝 заявка: [текст] — оставить заявку\n"
                "📋 список заявок — ваши заявки\n"
                "⏰ напомни — установить напоминание\n"
                "📊 статистика — статистика заявок\n"
                "❓ помощь — эта справка"
            )
        
        @self.dp.message_handler(text(["привет", "здравствуйте", "добрый день", "доброе утро", "добрый вечер"]))
        async def greeting_handler(ctx: Context):
            await ctx.reply(
                f"👋 Здравствуйте, {ctx.user.name}! Я ваш виртуальный секретарь.\n\n"
                "📋 Доступные команды:\n"
                "📝 заявка: [текст] — оставить заявку\n"
                "📋 список заявок — ваши заявки\n"
                "⏰ напомни — установить напоминание\n"
                "📊 статистика — статистика заявок\n"
                "❓ помощь — эта справка"
            )
        
        @self.dp.message_handler(text("помощь"))
        async def help_handler(ctx: Context):
            await ctx.reply(
                "❓ Помощь по командам:\n\n"
                "📝 заявка: [текст] — создать новую заявку\n"
                "📋 список заявок — показать ваши заявки\n"
                "⏰ напомни — установить напоминание\n"
                "📊 статистика — показать статистику\n"
                "❓ помощь — эта справка\n\n"
                "💡 Пример: заявка: Нужна консультация по проекту"
            )
        
        @self.dp.message_handler(text("статистика"))
        async def stats_handler(ctx: Context):
            user_apps = [a for a in self.applications if a['user_id'] == ctx.user_id]
            total_apps = len(self.applications)
            
            await ctx.reply(
                f"📊 Статистика:\n\n"
                f"📋 Всего заявок в системе: {total_apps}\n"
                f"👤 Ваших заявок: {len(user_apps)}\n"
                f"📝 Новых заявок: {len([a for a in user_apps if a['status'] == '📝 Новая'])}\n"
                f"⏰ Активных напоминаний: {len(self.reminders)}"
            )
        
        @self.dp.message_handler(text("напомни"))
        async def reminder_handler(ctx: Context):
            self.reminders[ctx.user_id] = datetime.now()
            await ctx.reply(
                "⏰ Напоминание установлено!\n"
                "🔔 Я напомню вам проверить заявки через час."
            )
        
        @self.dp.message_handler(text("список заявок"))
        async def list_applications_handler(ctx: Context):
            user_apps = [a for a in self.applications if a['user_id'] == ctx.user_id]
            
            if user_apps:
                apps_text = "📋 Ваши заявки:\n\n"
                for app in user_apps[-5:]:  # Последние 5
                    apps_text += f"🔸 #{app['id']} ({app['date']})\n"
                    apps_text += f"   {app['status']} {app['category']}\n"
                    apps_text += f"   📝 {app['text'][:50]}{'...' if len(app['text']) > 50 else ''}\n\n"
                await ctx.reply(apps_text)
            else:
                await ctx.reply("📭 У вас пока нет заявок.")
        
        @self.dp.message_handler(has_attachment(True))
        async def attachment_handler(ctx: Context):
            """
            Обрабатывает любое сообщение, содержащее вложения.
            Демонстрирует использование фильтра `has_attachment`.
            """
            attachment_types = [att.type for att in ctx.attachments]
            await ctx.reply(f"Вижу вложения! Типы: {', '.join(attachment_types)}. Сохраняю в архив.")
            print(f"User {ctx.user_id} sent attachments: {attachment_types}")
        
        @self.dp.message_handler()
        async def no_attachment_handler(ctx: Context):
            """Обрабатывает сообщения без вложений."""
            await ctx.reply("Это сообщение без вложений, я его проигнорирую.")
        
        @self.dp.message_handler()
        async def application_handler(ctx: Context):
            if ctx.text.startswith("заявка:"):
                application_text = ctx.text[7:].strip()
                if application_text:
                    app = {
                        "id": len(self.applications) + 1,
                        "user_id": ctx.user_id,
                        "user_name": ctx.user.name,
                        "text": application_text,
                        "status": "📝 Новая",
                        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                        "category": "📄 Общая"
                    }
                    self.applications.append(app)
                    await ctx.reply(
                        f"✅ Заявка #{app['id']} принята!\n"
                        f"📝 Текст: {application_text}\n"
                        f"📅 Дата: {app['date']}\n"
                        f"📊 Всего заявок: {len(self.applications)}"
                    )
                else:
                    await ctx.reply("❌ Пожалуйста, укажите текст заявки после двоеточия.")
            else:
                await ctx.reply(
                    "🤔 Не понимаю команду. Напишите 'помощь' для справки."
                )
    
    async def check_reminders(self):
        """Проверка напоминаний"""
        current_time = datetime.now()
        for user_id, reminder_time in list(self.reminders.items()):
            if (current_time - reminder_time).seconds > 3600:  # Через час
                await self.bot.send_message(
                    "🔔 Напоминание!\n"
                    "📋 Не забудьте проверить свои заявки.",
                    user_id=user_id
                )
                del self.reminders[user_id]
    
    async def run(self):
        """Запуск бота"""
        print("👔 Бот-секретарь запущен!")
        
        async with self.bot:
            me = await self.bot.get_me()
            print(f"🤖 Бот: {me['name']} (ID: {me['user_id']})")
            
            # Запускаем проверку напоминаний в фоне
            asyncio.create_task(self.reminder_loop())
            
            await self.bot.polling(
                dispatcher=self.dp,
                timeout=1,
                long_polling_timeout=30
            )
    
    async def reminder_loop(self):
        """Цикл проверки напоминаний"""
        while True:
            await self.check_reminders()
            await asyncio.sleep(60)  # Проверяем каждую минуту

async def main():
    bot = SecretaryBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Пример бота с возможностями v1.3
Демонстрирует новые функции: загрузка файлов, комбинированные фильтры, валидация
"""

import asyncio
import os
from maxbot import Bot
from maxbot.dispatcher import Dispatcher
from maxbot.filters import (
    command, text, regex, attachment_type, has_attachment,
    and_filter, or_filter, not_filter, time_filter, user_filter, custom_filter
)

async def main():
    # Загружаем токен из файла
    if not os.path.exists("token.txt"):
        print("Создайте файл token.txt с токеном бота")
        return
    
    with open("token.txt", "r", encoding="utf-8") as f:
        token = f.read().strip()
    
    bot = Bot(token)
    dispatcher = Dispatcher(bot)
    
    # --- Примеры комбинированных фильтров ---
    
    @dispatcher.message_handler(command("start"))
    async def start_command(ctx):
        await ctx.reply(
            "🚀 Бот v1.3 запущен!\n\n"
            "Доступные команды:\n"
            "/upload - загрузить файл\n"
            "/download - скачать файл\n"
            "/validate - проверить файл\n"
            "/filters - тест фильтров\n"
            "/help - справка"
        )
    
    @dispatcher.message_handler(command("help"))
    async def help_command(ctx):
        await ctx.reply(
            "📖 Справка по новым возможностям v1.3:\n\n"
            "🔧 **Загрузка файлов:**\n"
            "- /upload image <путь> - загрузить изображение\n"
            "- /upload video <путь> - загрузить видео\n"
            "- /upload audio <путь> - загрузить аудио\n"
            "- /upload file <путь> - загрузить документ\n\n"
            "📥 **Скачивание файлов:**\n"
            "- /download <file_id> - скачать файл\n"
            "- /download <file_id> <путь> - скачать в папку\n\n"
            "✅ **Валидация:**\n"
            "- /validate size <путь> - проверить размер\n"
            "- /validate format <тип> <путь> - проверить формат\n\n"
            "🎯 **Фильтры:**\n"
            "- /filters - тест комбинированных фильтров"
        )
    
    # --- Примеры загрузки файлов ---
    
    @dispatcher.message_handler(command("upload"))
    async def upload_handler(ctx):
        args = ctx.text.split()[1:] if len(ctx.text.split()) > 1 else []
        
        if len(args) < 2:
            await ctx.reply("Использование: /upload <тип> <путь>\nТипы: image, video, audio, file")
            return
        
        file_type, file_path = args[0], args[1]
        
        if not os.path.exists(file_path):
            await ctx.reply(f"❌ Файл не найден: {file_path}")
            return
        
        try:
            # Валидируем размер файла
            if not await bot.validate_file_size(file_path, max_size_mb=50):
                await ctx.reply("❌ Файл слишком большой (максимум 50MB)")
                return
            
            # Валидируем формат
            if not await bot.validate_file_format(file_path, file_type):
                supported = await bot.get_supported_formats(file_type)
                await ctx.reply(f"❌ Неподдерживаемый формат. Поддерживаемые: {', '.join(supported)}")
                return
            
            # Загружаем файл
            await ctx.reply(f"📤 Загружаю {file_type}...")
            
            if file_type == "image":
                result = await bot.upload_image(file_path)
            elif file_type == "video":
                result = await bot.upload_video(file_path)
            elif file_type == "audio":
                result = await bot.upload_audio(file_path)
            elif file_type == "file":
                result = await bot.upload_file(file_path)
            else:
                await ctx.reply("❌ Неподдерживаемый тип файла")
                return
            
            # Отправляем загруженный файл
            await bot.send_attachment(
                {
                    "type": file_type,
                    "payload": result,
                    "filename": os.path.basename(file_path)
                },
                chat_id=ctx.chat_id,
                caption=f"✅ Файл загружен: {os.path.basename(file_path)}"
            )
            
        except Exception as e:
            await ctx.reply(f"❌ Ошибка загрузки: {str(e)}")
    
    # --- Примеры скачивания файлов ---
    
    @dispatcher.message_handler(command("download"))
    async def download_handler(ctx):
        args = ctx.text.split()[1:] if len(ctx.text.split()) > 1 else []
        
        if len(args) < 1:
            await ctx.reply("Использование: /download <file_id> [путь_сохранения]")
            return
        
        file_id = args[0]
        save_path = args[1] if len(args) > 1 else None
        
        try:
            await ctx.reply(f"📥 Скачиваю файл {file_id}...")
            
            if save_path:
                result = await bot.download_file(file_id, save_path)
                await ctx.reply(f"✅ Файл сохранен: {result}")
            else:
                result = await bot.download_file(file_id)
                await ctx.reply(f"✅ Файл скачан, размер: {len(result)} байт")
                
        except Exception as e:
            await ctx.reply(f"❌ Ошибка скачивания: {str(e)}")
    
    # --- Примеры валидации ---
    
    @dispatcher.message_handler(command("validate"))
    async def validate_handler(ctx):
        args = ctx.text.split()[1:] if len(ctx.text.split()) > 2 else []
        
        if len(args) < 2:
            await ctx.reply("Использование: /validate <size|format> [тип] <путь>")
            return
        
        validation_type = args[0]
        
        if validation_type == "size":
            if len(args) < 2:
                await ctx.reply("Использование: /validate size <путь>")
                return
            
            file_path = args[1]
            
            if not os.path.exists(file_path):
                await ctx.reply(f"❌ Файл не найден: {file_path}")
                return
            
            try:
                is_valid = await bot.validate_file_size(file_path, max_size_mb=50)
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                
                if is_valid:
                    await ctx.reply(f"✅ Размер файла OK: {file_size:.2f} MB")
                else:
                    await ctx.reply(f"❌ Файл слишком большой: {file_size:.2f} MB (максимум 50MB)")
                    
            except Exception as e:
                await ctx.reply(f"❌ Ошибка проверки: {str(e)}")
        
        elif validation_type == "format":
            if len(args) < 3:
                await ctx.reply("Использование: /validate format <тип> <путь>")
                return
            
            file_type, file_path = args[1], args[2]
            
            if not os.path.exists(file_path):
                await ctx.reply(f"❌ Файл не найден: {file_path}")
                return
            
            try:
                is_valid = await bot.validate_file_format(file_path, file_type)
                supported = await bot.get_supported_formats(file_type)
                
                if is_valid:
                    await ctx.reply(f"✅ Формат файла поддерживается: {os.path.splitext(file_path)[1]}")
                else:
                    await ctx.reply(f"❌ Неподдерживаемый формат. Поддерживаемые: {', '.join(supported)}")
                    
            except Exception as e:
                await ctx.reply(f"❌ Ошибка проверки: {str(e)}")
    
    # --- Примеры комбинированных фильтров ---
    
    @dispatcher.message_handler(command("filters"))
    async def filters_test(ctx):
        await ctx.reply(
            "🎯 Тест комбинированных фильтров:\n\n"
            "Отправь:\n"
            "1. 'привет' - сработает text фильтр\n"
            "2. Фото - сработает attachment фильтр\n"
            "3. 'привет' + фото - сработает AND фильтр\n"
            "4. 'пока' ИЛИ 'до свидания' - сработает OR фильтр\n"
            "5. Любое сообщение НЕ с командой - сработает NOT фильтр"
        )
    
    # Комбинированные фильтры
    @dispatcher.message_handler(
        and_filter(
            text("привет"),
            has_attachment()
        )
    )
    async def hello_with_attachment(ctx):
        await ctx.reply("👋 Привет! И у тебя есть вложение!")
    
    @dispatcher.message_handler(
        or_filter(
            text("пока"),
            text("до свидания")
        )
    )
    async def goodbye_handler(ctx):
        await ctx.reply("👋 До свидания!")
    
    @dispatcher.message_handler(
        not_filter(command("start"))
    )
    async def not_start_command(ctx):
        if ctx.text and not ctx.text.startswith('/'):
            await ctx.reply("ℹ️ Это не команда /start")
    
    # Фильтр по времени
    @dispatcher.message_handler(
        and_filter(
            text("ночь"),
            time_filter(22, 6)  # С 22:00 до 06:00
        )
    )
    async def night_handler(ctx):
        await ctx.reply("🌙 Спокойной ночи!")
    
    # Фильтр по пользователю (замените на реальный ID)
    @dispatcher.message_handler(
        and_filter(
            text("admin"),
            user_filter([123456789])  # Замените на реальный ID
        )
    )
    async def admin_handler(ctx):
        await ctx.reply("🔐 Админ команда выполнена!")
    
    # Кастомный фильтр
    def is_long_message(ctx):
        return len(ctx.text or "") > 100
    
    @dispatcher.message_handler(
        custom_filter(is_long_message)
    )
    async def long_message_handler(ctx):
        await ctx.reply("📝 Длинное сообщение! Спасибо за подробность!")
    
    # --- Обработка вложений с валидацией ---
    
    @dispatcher.message_handler(has_attachment())
    async def attachment_handler(ctx):
        for attachment in ctx.attachments:
            attachment_type = attachment.type
            
            if attachment_type == "image":
                await ctx.reply(f"🖼️ Получил изображение: {attachment.filename or 'Без названия'}")
                
                # Можно скачать изображение
                # file_data = await bot.download_file(attachment.payload.photo_id)
                
            elif attachment_type == "file":
                filename = attachment.filename or "Без названия"
                size = attachment.size or 0
                await ctx.reply(f"📄 Файл: {filename} ({size} байт)")
                
            elif attachment_type == "video":
                duration = attachment.duration or 0
                await ctx.reply(f"🎥 Видео: {duration} секунд")
                
            elif attachment_type == "audio":
                performer = attachment.performer or "Неизвестный"
                title = attachment.title or "Без названия"
                await ctx.reply(f"🎵 Аудио: {performer} - {title}")
    
    # --- Обработчик по умолчанию ---
    
    @dispatcher.message_handler()
    async def default_handler(ctx):
        if ctx.text:
            await ctx.reply(f"💬 Вы сказали: {ctx.text}")
        else:
            await ctx.reply("📝 Получил сообщение без текста")
    
    # Запускаем бота
    print("🚀 Запускаю бота v1.3...")
    async with bot:
        await bot.polling(dispatcher=dispatcher)

if __name__ == "__main__":
    asyncio.run(main()) 
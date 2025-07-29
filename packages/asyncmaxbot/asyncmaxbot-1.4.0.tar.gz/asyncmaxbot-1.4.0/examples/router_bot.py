import asyncio
import logging

from maxbot import Bot, Dispatcher
from examples.handlers import user_commands, image_sender

# Замените на ваш токен
TOKEN = "f9LHodD0cOJWZKXqsPvxfkGOIdHYU259lh6esOnVwd7tN30GVF1UMHPmPeDUsBsioTwOXPbXA98rbMZZZYcn" 

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=TOKEN)
    dp = Dispatcher(bot)

    # Подключаем роутеры
    dp.include_router(user_commands.router)
    dp.include_router(image_sender.router)

    print("Роутер-бот запущен!")
    await bot.polling(dispatcher=dp)


if __name__ == "__main__":
    asyncio.run(main()) 
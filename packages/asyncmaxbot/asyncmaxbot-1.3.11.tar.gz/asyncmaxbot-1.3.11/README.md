[![PyPI - Version](https://img.shields.io/pypi/v/asyncmaxbot.svg)](https://pypi.org/project/asyncmaxbot/)
[![PyPI - License](https://img.shields.io/pypi/l/asyncmaxbot.svg)](https://github.com/sdkinfotech/asyncmaxbot/blob/main/LICENSE)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://sdkinfotech.github.io/asyncmaxbot/)

# Добро пожаловать в AsyncMaxBot SDK!

Это официальная документация по **AsyncMaxBot**, асинхронной Python-библиотеке для создания ботов в Max Messenger.

Здесь вы найдете всё необходимое для разработки ботов любой сложности: от простых эхо-ботов до продвинутых систем с комплексной логикой.

## Быстрый старт

Вот минимальный пример бота, который отвечает на команду `/start` и повторяет любое текстовое сообщение. Этот код полностью рабочий.

```python
import asyncio
from maxbot import Bot, Dispatcher, Context
from maxbot.filters import command

# Рекомендуется хранить токен в переменной окружения или в файле
TOKEN = "YOUR_TOKEN_HERE"

async def main():
    # Используем 'async with' для корректного управления сессией
    async with Bot(token=TOKEN) as bot:
        dp = Dispatcher(bot)

        # Обработчик команды /start
        @dp.message_handler(command("start"))
        async def handle_start(ctx: Context):
            # Используем .user.name для получения имени пользователя
            await ctx.reply(f"Привет, {ctx.user.name}!")

        # Обработчик для всех остальных текстовых сообщений
        @dp.message_handler()
        async def handle_echo(ctx: Context):
            if ctx.text:
                await ctx.reply(f"Вы написали: {ctx.text}")

        # Запускаем получение обновлений
        print("Бот запущен...")
        await bot.polling(dispatcher=dp)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
```

### Как запустить:
1.  Установите библиотеку: `pip install asyncmaxbot`
2.  Сохраните код в файл, например, `my_bot.py`.
3.  Замените `"YOUR_TOKEN_HERE"` на реальный токен вашего бота.
4.  Запустите его: `python my_bot.py`

## Куда двигаться дальше?

*   **[Руководство по API](https://sdkinfotech.github.io/asyncmaxbot/api/):** Перейдите сюда для подробного изучения всех компонентов, классов и методов SDK.
*   **[Примеры кода](https://sdkinfotech.github.io/asyncmaxbot/examples/):** Изучите новую страницу с "живыми" примерами кода.
*   **[Страница проекта на PyPI](https://pypi.org/project/asyncmaxbot/):** Посетите страницу проекта для получения информации об установке и версиях.
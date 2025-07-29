# AsyncMaxBot SDK

[![PyPI version](https://badge.fury.io/py/asyncmaxbot.svg)](https://badge.fury.io/py/asyncmaxbot)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docs](https://img.shields.io/badge/docs-passing-brightgreen)](https://sdkinfotech.github.io/asyncmaxbot/)

**AsyncMaxBot SDK** — это современная, асинхронная и удобная библиотека на языке Python для создания ботов для Max Messenger. Она предоставляет полный набор инструментов для взаимодействия с [официальным API Max](https://dev.max.ru/docs-api), позволяя разработчикам сосредоточиться на логике бота, а не на низкоуровневых деталях API.

Библиотека разработана с учетом лучших практик асинхронного программирования и предлагает интуитивно понятный интерфейс, вдохновленный популярными фреймворками.

---

## ✨ Ключевые возможности

- **Полная асинхронность**: Построена на `asyncio` и `aiohttp` для максимальной производительности.
- **Мощные фильтры (`F`)**: Создавайте сложные правила для обработки сообщений с помощью Magic-фильтров.
- **Router-система**: Организуйте код в виде модулей для лучшей читаемости и поддержки.
- **Middleware**: Добавляйте собственную логику в процесс обработки обновлений.
- **Интерактивные клавиатуры**: Легко создавайте inline-кнопки и обрабатывайте callback-запросы.
- **Строгая типизация**: Все объекты API валидируются с помощью Pydantic для надежности вашего кода.
- **Обработка событий**: Реагируйте на системные события, такие как добавление пользователя в чат.

---

## 🚀 Быстрый старт

Вот пример простого эхо-бота, который также приветствует пользователя по команде `/start`.

**1. Установите библиотеку:**
```bash
pip install asyncmaxbot
```

**2. Напишите код вашего бота:**
```python
# bot.py
import asyncio
from maxbot import Bot, Dispatcher, Context, F

# Рекомендуется хранить токен в переменной окружения
TOKEN = "YOUR_TOKEN_HERE"

async def main():
    # Используем 'async with' для корректного управления сессией
    async with Bot(token=TOKEN) as bot:
        dp = Dispatcher(bot)

        # 1. Обработчик команды /start
        @dp.message_handler(F.command == "start")
        async def handle_start(ctx: Context):
            await ctx.reply(f"👋 Привет, {ctx.user.name}!")

        # 2. Обработчик для всех остальных текстовых сообщений
        @dp.message_handler(F.text)
        async def handle_echo(ctx: Context):
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

**3. Запустите бота:**
```bash
python bot.py
```

---

## 📚 Документация

Полное руководство по всем компонентам, классам и методам SDK доступно на нашем сайте документации:

### ➡️ **[Перейти к документации](https://sdkinfotech.github.io/asyncmaxbot/)**

На сайте вы найдете:
- Подробное **Руководство по API**.
- Коллекцию **рабочих примеров**, от простых до продвинутых.
- Лучшие практики по **структуре проекта**.

---

## 🔗 Официальные ресурсы Max Messenger

- **[Портал для разработчиков](https://dev.max.ru/docs)** — общая документация по платформе.
- **[Справочник по Bot API](https://dev.max.ru/docs-api)** — детальное описание всех методов API.
- **[Центр помощи](https://dev.max.ru/help)** — ответы на часто задаваемые вопросы.

---

## 🤝 Вклад в проект (Contributing)

Мы всегда рады помощи в развитии библиотеки! Если вы хотите внести свой вклад, пожалуйста, следуйте этим шагам.

### Для разработчиков
1.  **Форкните** репозиторий.
2.  Создайте новую ветку для вашей функциональности (`git checkout -b feature/AmazingFeature`).
3.  Внесите свои изменения и закоммитьте их (`git commit -m 'Add some AmazingFeature'`).
4.  Отправьте изменения в свой форк (`git push origin feature/AmazingFeature`).
5.  Создайте **Pull Request**.

### Для AI-ассистентов
Для автоматизации рутинных задач и соблюдения стандартов кодирования, пожалуйста, ознакомьтесь с руководством в файле **[AI_GUIDE.md](AI_GUIDE.md)**.
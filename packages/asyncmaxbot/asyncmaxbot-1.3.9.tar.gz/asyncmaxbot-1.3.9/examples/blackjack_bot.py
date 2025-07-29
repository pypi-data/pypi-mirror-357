"""
Блэкджек бот - стандартная архитектура
Демонстрирует работу с игровым состоянием
"""

import asyncio
import os
import random
from maxbot import Bot
from maxbot.dispatcher import Dispatcher
from maxbot.filters import command, text
from maxbot.middleware import MiddlewareManager, LoggingMiddleware, ErrorHandlingMiddleware
from maxbot.max_types import Context

TOKEN = "YOUR_TOKEN_HERE"  # Замените на ваш токен

# Карты для игры
CARDS = {
    '2♠': 2, '3♠': 3, '4♠': 4, '5♠': 5, '6♠': 6, '7♠': 7, '8♠': 8, '9♠': 9, '10♠': 10, 'J♠': 10, 'Q♠': 10, 'K♠': 10, 'A♠': 11,
    '2♣': 2, '3♣': 3, '4♣': 4, '5♣': 5, '6♣': 6, '7♣': 7, '8♣': 8, '9♣': 9, '10♣': 10, 'J♣': 10, 'Q♣': 10, 'K♣': 10, 'A♣': 11,
    '2♥': 2, '3♥': 3, '4♥': 4, '5♥': 5, '6♥': 6, '7♥': 7, '8♥': 8, '9♥': 9, '10♥': 10, 'J♥': 10, 'Q♥': 10, 'K♥': 10, 'A♥': 11,
    '2♦': 2, '3♦': 3, '4♦': 4, '5♦': 5, '6♦': 6, '7♦': 7, '8♦': 8, '9♦': 9, '10♦': 10, 'J♦': 10, 'Q♦': 10, 'K♦': 10, 'A♦': 11
}

class BlackjackGame:
    """Класс для игры в блэкджек"""
    
    def __init__(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name
        self.deck = list(CARDS.keys())
        random.shuffle(self.deck)
        self.player_hand = []
        self.dealer_hand = []
        self.game_over = False
        self.result = ""
        
        # Раздача начальных карт
        self.player_hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())
        self.player_hand.append(self.deck.pop())
        self.dealer_hand.append(self.deck.pop())
    
    def get_hand_value(self, hand):
        """Подсчет очков в руке"""
        value = 0
        aces = 0
        
        for card in hand:
            card_value = CARDS[card]
            if card_value == 11:  # Туз
                aces += 1
            else:
                value += card_value
        
        # Добавляем тузы
        for _ in range(aces):
            if value + 11 <= 21:
                value += 11
            else:
                value += 1
        
        return value
    
    def hit(self):
        """Взять карту"""
        if not self.game_over:
            self.player_hand.append(self.deck.pop())
            player_value = self.get_hand_value(self.player_hand)
            
            if player_value > 21:
                self.game_over = True
                self.result = "💥 Перебор! Вы проиграли!"
            elif player_value == 21:
                self.stand()
    
    def stand(self):
        """Остановиться"""
        if not self.game_over:
            self.game_over = True
            
            # Дилер берет карты до 17
            while self.get_hand_value(self.dealer_hand) < 17:
                self.dealer_hand.append(self.deck.pop())
            
            player_value = self.get_hand_value(self.player_hand)
            dealer_value = self.get_hand_value(self.dealer_hand)
            
            if dealer_value > 21:
                self.result = "🎉 Дилер перебрал! Вы выиграли!"
            elif player_value > dealer_value:
                self.result = "🎉 Вы выиграли!"
            elif player_value < dealer_value:
                self.result = "😔 Дилер выиграл!"
            else:
                self.result = "🤝 Ничья!"
    
    def get_game_state(self):
        """Получить состояние игры"""
        player_value = self.get_hand_value(self.player_hand)
        dealer_value = self.get_hand_value(self.dealer_hand)
        
        state = f"🎰 Блэкджек - {self.user_name}\n\n"
        
        # Карты дилера
        if self.game_over:
            state += f"🃏 Дилер: {' '.join(self.dealer_hand)} = {dealer_value}\n"
        else:
            state += f"🃏 Дилер: {self.dealer_hand[0]} ?\n"
        
        # Карты игрока
        state += f"👤 Вы: {' '.join(self.player_hand)} = {player_value}\n\n"
        
        if self.game_over:
            state += f"🏁 {self.result}\n\n"
            state += "🔄 /start - новая игра"
        else:
            state += "🎯 Ваши действия:\n"
            state += "📥 /hit - взять карту\n"
            state += "✋ /stand - остановиться"
        
        return state

class BlackjackBot:
    """
    Бот для игры в Блэкджек.

    Демонстрирует:
    - Управление состоянием игры (карты, счет) внутри класса.
    - Использование текстовых фильтров `Text` с `ignore_case=True`.
    - Простую игровую логику и взаимодействие с пользователем.
    """
    
    def __init__(self):
        self.bot = Bot(TOKEN)
        self.dp = Dispatcher(self.bot)
        self.setup_middleware()
        self.setup_handlers()
        self.active_games = {}
    
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
            # Начало новой игры
            if ctx.user_id in self.active_games:
                del self.active_games[ctx.user_id]
            
            game = BlackjackGame(ctx.user_id, ctx.user.name)
            self.active_games[ctx.user_id] = game
            
            await ctx.reply(
                f"🎰 Добро пожаловать в Блэкджек, {ctx.user.name}!\n\n"
                "🎯 Цель: набрать 21 очко или ближе к 21, чем дилер\n"
                "🃏 Туз = 1 или 11, Картинки = 10\n\n" +
                game.get_game_state()
            )
        
        @self.dp.message_handler(command("hit"))
        async def hit_handler(ctx: Context):
            if ctx.user_id in self.active_games:
                game = self.active_games[ctx.user_id]
                game.hit()
                await ctx.reply(game.get_game_state())
                
                if game.game_over:
                    del self.active_games[ctx.user_id]
            else:
                await ctx.reply(
                    "❌ Нет активной игры. Напишите /start для начала."
                )
        
        @self.dp.message_handler(command("stand"))
        async def stand_handler(ctx: Context):
            if ctx.user_id in self.active_games:
                game = self.active_games[ctx.user_id]
                game.stand()
                await ctx.reply(game.get_game_state())
                del self.active_games[ctx.user_id]
            else:
                await ctx.reply(
                    "❌ Нет активной игры. Напишите /start для начала."
                )
        
        @self.dp.message_handler(command("help"))
        async def help_handler(ctx: Context):
            await ctx.reply(
                "📖 Правила Блэкджека:\n\n"
                "🎯 Цель: набрать 21 очко или ближе к 21, чем дилер\n\n"
                "🃏 Значения карт:\n"
                "• 2-10 = номинал карты\n"
                "• J, Q, K = 10 очков\n"
                "• Туз = 1 или 11 (автоматически выбирается лучшее значение)\n\n"
                "🎮 Команды:\n"
                "• /start - начать новую игру\n"
                "• /hit - взять карту\n"
                "• /stand - остановиться\n"
                "• /help - эта справка"
            )
        
        @self.dp.message_handler(command("stats"))
        async def stats_handler(ctx: Context):
            active_games = len(self.active_games)
            await ctx.reply(
                f"📊 Статистика:\n\n"
                f"🎮 Активных игр: {active_games}\n"
                f"🃏 Карт в колоде: {len(CARDS)}\n"
                f"👥 Игроков онлайн: {len(set(game.user_id for game in self.active_games.values()))}\n\n"
                f"🎯 Начните игру: /start"
            )
        
        @self.dp.message_handler(text(["начать", "играть", "блэкджек"]))
        async def start_text_handler(ctx: Context):
            # Алиас для начала игры
            if ctx.user_id in self.active_games:
                del self.active_games[ctx.user_id]
            
            game = BlackjackGame(ctx.user_id, ctx.user.name)
            self.active_games[ctx.user_id] = game
            
            await ctx.reply(
                f"🎰 Начинаем игру, {ctx.user.name}!\n\n" +
                game.get_game_state()
            )
        
        @self.dp.message_handler(text(["карта", "еще", "hit"]))
        async def hit_text_handler(ctx: Context):
            if ctx.user_id in self.active_games:
                game = self.active_games[ctx.user_id]
                game.hit()
                await ctx.reply(game.get_game_state())
                
                if game.game_over:
                    del self.active_games[ctx.user_id]
            else:
                await ctx.reply("❌ Нет активной игры. Напишите 'начать' для начала.")
        
        @self.dp.message_handler(text(["стоп", "хватит", "stand"]))
        async def stand_text_handler(ctx: Context):
            if ctx.user_id in self.active_games:
                game = self.active_games[ctx.user_id]
                game.stand()
                await ctx.reply(game.get_game_state())
                del self.active_games[ctx.user_id]
            else:
                await ctx.reply("❌ Нет активной игры. Напишите 'начать' для начала.")
        
        @self.dp.message_handler()
        async def default_handler(ctx: Context):
            if ctx.user_id in self.active_games:
                game = self.active_games[ctx.user_id]
                await ctx.reply(
                    f"🤔 Не понимаю команду. Вот ваша игра:\n\n" + game.get_game_state()
                )
            else:
                await ctx.reply(
                    "🎰 Добро пожаловать в Блэкджек!\n\n"
                    "🎮 Доступные команды:\n"
                    "🎰 /start - начать игру\n"
                    "📖 /help - правила\n"
                    "📊 /stats - статистика\n\n"
                    "🎯 Готовы играть?"
                )
    
    async def run(self):
        """Запуск бота"""
        print("🎰 Блэкджек бот запущен!")
        
        async with self.bot:
            me = await self.bot.get_me()
            print(f"🤖 Бот: {me['name']} (ID: {me['user_id']})")
            
            await self.bot.polling(
                dispatcher=self.dp,
                timeout=1,
                long_polling_timeout=30
            )

async def main():
    bot = BlackjackBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Интеграция основного бота 🎰 с UserBot для выплат звёзд
"""

import asyncio
import random
from typing import Optional
from datetime import datetime
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class StarsGameBot:
    """
    Основной бот игры 🎰 с интеграцией UserBot для выплат звёзд
    """

    def __init__(self):
        self.bot_token = os.getenv("BOT_TOKEN")
        self.userbot_api_url = "http://localhost:8000"  # API endpoint UserBot

        # Настройки игры
        self.spin_cost = 15  # Стоимость спина в звёздах
        self.symbols = ['🍒', '🍋', '🍊', '🍇', '⭐', '💎', '7️⃣']

        # Таблица выплат
        self.payouts = {
            '7️⃣': 100,  # Джекпот
            '💎': 50,
            '⭐': 20,
            '🍇': 10,
            '🍊': 8,
            '🍋': 5,
            '🍒': 3
        }

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user

        welcome_message = f"""
🎰 **Добро пожаловать в Telegram Stars Rewards!**

Привет, {user.first_name}!

**Как играть:**
• Стоимость одной игры: {self.spin_cost} звёзд
• Выигрыш при совпадении 3 символов
• Моментальная выплата в звёздах!

**Таблица выплат (за {self.spin_cost} звёзд):**
7️⃣7️⃣7️⃣ = {self.spin_cost * self.payouts['7️⃣']} звёзд
💎💎💎 = {self.spin_cost * self.payouts['💎']} звёзд
⭐⭐⭐ = {self.spin_cost * self.payouts['⭐']} звёзд

**Команды:**
/play - Играть ({self.spin_cost} звёзд)
/stats - Ваша статистика
/help - Помощь

Удачи! 🍀
        """

        keyboard = [
            [InlineKeyboardButton(f"🎰 ИГРАТЬ ({self.spin_cost}⭐)", callback_data="spin")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            welcome_message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    async def handle_spin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка игры 🎰"""
        query = update.callback_query
        user = query.from_user

        await query.answer()

        # Здесь должна быть проверка оплаты через Telegram Stars API
        # Для демо пропускаем

        # Анимация спина
        animation_message = await query.message.reply_text("🎰 Крутим барабаны...")

        for _ in range(3):
            symbols = [random.choice(self.symbols) for _ in range(3)]
            await animation_message.edit_text(f"🎰 {' '.join(symbols)}")
            await asyncio.sleep(0.5)

        # Финальный результат
        result = self.generate_spin_result()
        final_symbols = result['symbols']

        await animation_message.edit_text(f"🎰 **{' '.join(final_symbols)}**", parse_mode="Markdown")

        # Проверка выигрыша
        if result['is_win']:
            win_amount = result['amount']

            # Отправляем запрос на выплату UserBot
            payout_success = await self.request_payout(
                user_id=user.id,
                username=user.username,
                amount=win_amount
            )

            if payout_success:
                await query.message.reply_text(
                    f"""
🎉 **ПОЗДРАВЛЯЕМ!**

Вы выиграли **{win_amount} звёзд**!

✨ Выплата будет отправлена в течение 30-60 секунд.
📨 Проверьте входящие сообщения!

Хотите сыграть ещё?
                    """,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"🎰 ИГРАТЬ ЕЩЁ ({self.spin_cost}⭐)", callback_data="spin")]
                    ])
                )
            else:
                await query.message.reply_text(
                    "⚠️ Произошла ошибка при обработке выплаты. Администратор уведомлён."
                )
        else:
            await query.message.reply_text(
                f"""
😔 Не повезло в этот раз!

Попробуйте ещё раз - удача улыбнётся вам!
                """,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"🎰 ИГРАТЬ ЕЩЁ ({self.spin_cost}⭐)", callback_data="spin")]
                ])
            )

    def generate_spin_result(self) -> dict:
        """Генерация результата спина с учётом RTP"""

        # RTP 95% - настраиваемый параметр
        rtp = 0.95
        win_chance = rtp / len(self.symbols)  # Упрощённая формула

        if random.random() < win_chance:
            # Выигрыш
            symbol = random.choices(
                list(self.payouts.keys()),
                weights=[1, 2, 3, 4, 5, 6, 0.5],  # Веса для разных символов
                k=1
            )[0]

            return {
                'symbols': [symbol, symbol, symbol],
                'is_win': True,
                'amount': self.spin_cost * self.payouts[symbol]
            }
        else:
            # Проигрыш
            symbols = []
            while len(set(symbols)) != 3:  # Гарантируем разные символы
                symbols = [random.choice(self.symbols) for _ in range(3)]

            return {
                'symbols': symbols,
                'is_win': False,
                'amount': 0
            }

    async def request_payout(self, user_id: int, username: str, amount: int) -> bool:
        """Отправка запроса на выплату UserBot"""
        try:
            game_id = f"game_{user_id}_{datetime.now().timestamp()}"

            # Отправляем запрос UserBot через API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.userbot_api_url}/payout",
                    json={
                        "user_id": user_id,
                        "username": username,
                        "amount": amount,
                        "game_id": game_id
                    }
                ) as response:
                    result = await response.json()
                    return result.get("success", False)

        except Exception as e:
            logger.error(f"Ошибка отправки запроса на выплату: {e}")
            return False

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats"""
        user = update.effective_user

        # Здесь должна быть загрузка статистики из БД
        stats_message = f"""
📊 **Ваша статистика**

Игрок: {user.first_name}
Всего игр: 0
Выиграно: 0 звёзд
Проиграно: 0 звёзд

_Статистика обновляется после каждой игры_
        """

        await update.message.reply_text(stats_message, parse_mode="Markdown")

def main():
    """Запуск основного бота"""

    # Создаём приложение
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    bot = StarsGameBot()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("stats", bot.stats_command))
    application.add_handler(CallbackQueryHandler(bot.handle_spin, pattern="spin"))

    print("""
╔══════════════════════════════════════════════════════════╗
║              TELEGRAM STARS REWARDS BOT 🎰              ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Основной бот запущен!                                  ║
║                                                          ║
║  Убедитесь, что UserBot также запущен для выплат звёзд. ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
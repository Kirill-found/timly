"""
Бот для группы @StarzLoot - игра 🎰 с выплатами звёзд
Пользователи отправляют dice прямо в группу
"""

import os
import asyncio
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters
from dotenv import load_dotenv
from game_logic import GameLogic
from database import Database

# Загрузка настроек
load_dotenv()

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Настройки
ADMIN_ID = int(os.getenv('ADMIN_ID', '517682186'))
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', 'StarzLoot')
CHANNEL_LINK = os.getenv('CHANNEL_LINK', 'https://t.me/StarzLoot')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///game_bot.db')

class GroupGameBot:
    """Бот для группы - обработка dice игр"""

    def __init__(self):
        self.db = Database(DATABASE_URL)
        self.game_logic = GameLogic(self.db)
        self.admin_id = ADMIN_ID

    async def handle_dice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка dice эмодзи в группе"""

        # Проверяем что это dice 🎰
        if not update.message.dice or update.message.dice.emoji != "🎰":
            return

        user = update.effective_user
        chat = update.effective_chat
        dice_value = update.message.dice.value

        logger.info(f"Игра от {user.id} (@{user.username}), dice_value: {dice_value}")

        # Ждём анимацию dice
        await asyncio.sleep(3)

        # Проверяем выигрыш
        result = self.game_logic.check_win(dice_value)

        if result['win']:
            # ВЫИГРЫШ!
            win_amount = result['payout']
            combo = result['combo_emoji']

            logger.info(f"✅ ВЫИГРЫШ! User {user.id}, Amount: {win_amount}, Combo: {combo}")

            # Сохраняем в базу
            try:
                await self.db.add_payout(
                    user_id=user.id,
                    username=user.username,
                    amount=win_amount,
                    game_type='dice'
                )
            except Exception as e:
                logger.error(f"Ошибка сохранения в БД: {e}")

            # Сообщение в группу
            await update.message.reply_text(
                f"🎉 ПОЗДРАВЛЯЕМ @{user.username or user.first_name}!\n\n"
                f"{combo}\n"
                f"Вы выиграли {win_amount} звёзд! ⭐\n\n"
                f"Выплата будет отправлена в течение 1-2 минут."
            )

            # Уведомление админу
            try:
                admin_message = (
                    f"🎰 **ТРЕБУЕТСЯ ВЫПЛАТА!**\n\n"
                    f"Игрок: @{user.username or 'NoUsername'}\n"
                    f"Имя: {user.first_name}\n"
                    f"ID: `{user.id}`\n"
                    f"Выигрыш: **{win_amount} звёзд** ⭐\n"
                    f"Комбинация: {combo}\n"
                    f"Группа: @{CHANNEL_USERNAME}\n\n"
                    f"**Как выплатить:**\n"
                    f"1. Найдите пользователя: "
                )

                # Добавляем ссылку на пользователя
                if user.username:
                    admin_message += f"@{user.username}\n"
                else:
                    admin_message += f"[Открыть профиль](tg://user?id={user.id})\n"

                admin_message += (
                    f"2. Профиль → Меню (⋮) → Отправить подарок\n"
                    f"3. Выберите {win_amount} звёзд\n"
                    f"4. Отправьте"
                )

                await context.bot.send_message(
                    self.admin_id,
                    admin_message,
                    parse_mode='Markdown'
                )

                logger.info(f"✅ Уведомление отправлено админу")

            except Exception as e:
                logger.error(f"❌ Ошибка отправки уведомления админу: {e}")
                # Пробуем отправить без Markdown
                try:
                    await context.bot.send_message(
                        self.admin_id,
                        f"ТРЕБУЕТСЯ ВЫПЛАТА!\n\n"
                        f"Игрок: @{user.username or user.first_name}\n"
                        f"ID: {user.id}\n"
                        f"Сумма: {win_amount} звёзд\n"
                        f"Комбинация: {combo}"
                    )
                except Exception as e2:
                    logger.error(f"❌ Ошибка повторной отправки: {e2}")

        else:
            # Проигрыш - ничего не делаем или опционально:
            logger.info(f"Проигрыш: User {user.id}, dice_value: {dice_value}")
            # Можно добавить реакцию или просто ничего не делать

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats - статистика игрока"""
        user = update.effective_user

        try:
            stats = await self.db.get_user_stats(user.id)

            if stats:
                await update.message.reply_text(
                    f"📊 Ваша статистика:\n\n"
                    f"Всего игр: {stats.get('total_games', 0)}\n"
                    f"Выиграно: {stats.get('total_won', 0)} звёзд\n"
                    f"Баланс: {stats.get('balance', 0)} звёзд"
                )
            else:
                await update.message.reply_text(
                    "📊 У вас пока нет статистики.\n"
                    "Отправьте 🎰 для игры!"
                )
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            await update.message.reply_text("Статистика временно недоступна")

    async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Админская статистика"""
        if update.effective_user.id != self.admin_id:
            return

        try:
            stats = await self.db.get_global_stats()

            await update.message.reply_text(
                f"📊 **СТАТИСТИКА СИСТЕМЫ**\n\n"
                f"Всего игроков: {stats.get('total_players', 0)}\n"
                f"Всего игр: {stats.get('total_games', 0)}\n"
                f"Выплачено: {stats.get('total_payouts', 0)} звёзд\n"
                f"Прибыль: {stats.get('profit', 0)} звёзд",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            await update.message.reply_text("Статистика временно недоступна")

    async def rules_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Правила игры"""
        await update.message.reply_text(
            f"🎰 **Правила игры @{CHANNEL_USERNAME}**\n\n"
            f"1️⃣ Отправьте 🎰 в группу\n"
            f"2️⃣ Дождитесь результата\n"
            f"3️⃣ При совпадении 3 символов - выигрыш!\n\n"
            f"**Таблица выплат:**\n"
            f"🍒🍒🍒 = 100 звёзд\n"
            f"🍋🍋🍋 = 200 звёзд\n"
            f"🍇🍇🍇 = 350 звёзд\n"
            f"7️⃣7️⃣7️⃣ = 500 звёзд\n\n"
            f"Удачи! 🍀",
            parse_mode='Markdown'
        )

def main():
    """Запуск бота"""

    print("\n" + "="*60)
    print(f"    ЗАПУСК БОТА ДЛЯ ГРУППЫ @{CHANNEL_USERNAME}")
    print("="*60)

    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()

    bot = GroupGameBot()

    # Обработчики
    application.add_handler(MessageHandler(filters.Dice.SLOT_MACHINE, bot.handle_dice))
    application.add_handler(CommandHandler("stats", bot.stats_command))
    application.add_handler(CommandHandler("admin", bot.admin_stats))
    application.add_handler(CommandHandler("rules", bot.rules_command))

    print(f"\n[OK] Бот запущен!")
    print(f"[OK] Группа/канал: @{CHANNEL_USERNAME}")
    print(f"[OK] Ожидание dice от игроков...")
    print(f"\n[!] Убедитесь что бот добавлен в группу @{CHANNEL_USERNAME}")
    print(f"[!] И имеет права: читать сообщения, отправлять сообщения\n")
    print("="*60 + "\n")

    logger.info(f"Бот для группы @{CHANNEL_USERNAME} запущен")

    # Запускаем
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

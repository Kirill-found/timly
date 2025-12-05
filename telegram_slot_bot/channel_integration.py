"""
Интеграция с каналом @StarzLoot для выплат звёзд
"""

import os
import asyncio
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from database import Database
from game_logic import GameLogic
import random

# Загрузка настроек
load_dotenv()

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', 'StarzLoot')
CHANNEL_LINK = os.getenv('CHANNEL_LINK', 'https://t.me/StarzLoot')
ADMIN_ID = int(os.getenv('ADMIN_ID', '517682186'))
MESSAGE_COST = 20  # Стоимость игры в звёздах

class StarsRewardsChannelBot:
    """
    Бот для канала StarzLoot - выплаты звёзд через игру 🎰
    """

    def __init__(self):
        self.db = Database(os.getenv('DATABASE_URL'))
        self.game_logic = GameLogic(self.db)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user = update.effective_user

        # Проверяем, подписан ли пользователь на канал
        try:
            member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user.id)
            is_member = member.status in ['member', 'administrator', 'creator']
        except:
            is_member = False

        if not is_member:
            # Пользователь не подписан на канал
            keyboard = [
                [InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK)],
                [InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"🎰 **Добро пожаловать в Stars Rewards!**\n\n"
                f"Для участия в розыгрыше звёзд необходимо:\n"
                f"1️⃣ Подписаться на канал {CHANNEL_LINK}\n"
                f"2️⃣ Нажать кнопку 'Я подписался'\n\n"
                f"После подписки вы сможете играть и выигрывать звёзды! ⭐",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            # Пользователь подписан
            keyboard = [
                [InlineKeyboardButton(f"🎰 Играть ({MESSAGE_COST} звёзд)", callback_data="play_game")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"🎰 **Добро пожаловать, {user.first_name}!**\n\n"
                f"✅ Вы подписаны на канал!\n\n"
                f"**Правила игры:**\n"
                f"• Стоимость одной игры: {MESSAGE_COST} звёзд\n"
                f"• Отправьте 🎰 для игры\n"
                f"• При совпадении 3 символов - выигрыш!\n\n"
                f"**Таблица выплат:**\n"
                f"7️⃣7️⃣7️⃣ = 500 звёзд\n"
                f"🍇🍇🍇 = 350 звёзд\n"
                f"🍋🍋🍋 = 200 звёзд\n"
                f"🍒🍒🍒 = 100 звёзд\n\n"
                f"Удачной игры! 🍀",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )

    async def check_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Проверка подписки на канал"""
        query = update.callback_query
        user = query.from_user

        await query.answer()

        try:
            member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user.id)
            is_member = member.status in ['member', 'administrator', 'creator']
        except:
            is_member = False

        if is_member:
            keyboard = [
                [InlineKeyboardButton(f"🎰 Играть ({MESSAGE_COST} звёзд)", callback_data="play_game")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"✅ **Отлично, {user.first_name}!**\n\n"
                f"Вы успешно подписались на канал.\n"
                f"Теперь вы можете играть и выигрывать звёзды!\n\n"
                f"Нажмите кнопку ниже для игры 🎰",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK)],
                [InlineKeyboardButton("✅ Я подписался", callback_data="check_subscription")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "❌ Вы ещё не подписаны на канал.\n\n"
                "Пожалуйста, подпишитесь и попробуйте снова.",
                reply_markup=reply_markup
            )

    async def handle_dice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка dice эмодзи 🎰"""
        if update.message.dice and update.message.dice.emoji == "🎰":
            user = update.effective_user
            dice_value = update.message.dice.value

            # Проверяем подписку
            try:
                member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user.id)
                is_member = member.status in ['member', 'administrator', 'creator']
            except:
                is_member = False

            if not is_member:
                await update.message.reply_text(
                    "❌ Необходимо подписаться на канал для игры!\n"
                    f"Подпишитесь: {CHANNEL_LINK}"
                )
                return

            # Ждём анимацию dice
            await asyncio.sleep(3)

            # Проверяем выигрыш
            result = self.game_logic.check_win(dice_value)

            if result['win']:
                # ВЫИГРЫШ!
                win_amount = result['payout']
                combo = result['combo_emoji']

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

                # Уведомляем пользователя
                await update.message.reply_text(
                    f"🎉 **ПОЗДРАВЛЯЕМ!**\n\n"
                    f"{combo}\n"
                    f"Вы выиграли **{win_amount} звёзд!** ⭐\n\n"
                    f"Выплата будет отправлена в течение 1-2 минут.",
                    parse_mode='Markdown'
                )

                # Уведомляем админа
                try:
                    await context.bot.send_message(
                        ADMIN_ID,
                        f"🎰 **ТРЕБУЕТСЯ ВЫПЛАТА**\n\n"
                        f"Игрок: @{user.username or 'NoUsername'}\n"
                        f"ID: `{user.id}`\n"
                        f"Выигрыш: **{win_amount} звёзд** ⭐\n"
                        f"Комбинация: {combo}\n\n"
                        f"**Как выплатить:**\n"
                        f"1. Найдите пользователя @{user.username or f'tg://user?id={user.id}'}\n"
                        f"2. Профиль → Отправить подарок\n"
                        f"3. Выберите {win_amount} звёзд",
                        parse_mode='Markdown'
                    )
                    logger.info(f"✅ Уведомление о выплате отправлено! User: {user.id}, Amount: {win_amount}")
                except Exception as e:
                    logger.error(f"❌ Ошибка отправки уведомления: {e}")
            else:
                # Проигрыш
                await update.message.reply_text(
                    f"😔 Не повезло в этот раз!\n\n"
                    f"Попробуйте ещё раз - удача улыбнётся вам! 🍀",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"🎰 Играть снова ({MESSAGE_COST} звёзд)", callback_data="play_game")]
                    ])
                )

    async def play_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатия кнопки играть"""
        query = update.callback_query
        await query.answer()

        await query.edit_message_text(
            f"🎰 **Отправьте dice эмодзи в чат!**\n\n"
            f"Просто нажмите на 🎰 в меню эмодзи\n"
            f"или скопируйте и отправьте: 🎰\n\n"
            f"Стоимость игры: {MESSAGE_COST} звёзд",
            parse_mode='Markdown'
        )

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать статистику игрока"""
        user = update.effective_user

        # Получаем статистику из базы
        stats = await self.db.get_user_stats(user.id)

        if stats:
            await update.message.reply_text(
                f"📊 **Ваша статистика**\n\n"
                f"Всего игр: {stats.get('total_games', 0)}\n"
                f"Выиграно: {stats.get('total_won', 0)} звёзд\n"
                f"Проиграно: {stats.get('total_lost', 0)} звёзд\n"
                f"Баланс: {stats.get('balance', 0)} звёзд\n\n"
                f"Удачи в игре! 🍀",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "📊 У вас пока нет статистики.\n"
                "Сыграйте первую игру!"
            )

    async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Админская статистика"""
        if update.effective_user.id != ADMIN_ID:
            return

        stats = await self.db.get_global_stats()

        await update.message.reply_text(
            f"📊 **СТАТИСТИКА СИСТЕМЫ**\n\n"
            f"Всего игроков: {stats.get('total_players', 0)}\n"
            f"Всего игр: {stats.get('total_games', 0)}\n"
            f"Выплачено звёзд: {stats.get('total_payouts', 0)}\n"
            f"Собрано звёзд: {stats.get('total_collected', 0)}\n"
            f"Прибыль: {stats.get('profit', 0)} звёзд\n\n"
            f"RTP: {stats.get('rtp', 0):.2f}%",
            parse_mode='Markdown'
        )

def main():
    """Запуск бота"""
    # Создаём приложение
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    bot = StarsRewardsChannelBot()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("stats", bot.stats))
    application.add_handler(CommandHandler("admin", bot.admin_stats))
    application.add_handler(CallbackQueryHandler(bot.check_subscription, pattern="check_subscription"))
    application.add_handler(CallbackQueryHandler(bot.play_game, pattern="play_game"))
    application.add_handler(MessageHandler(filters.Dice.SLOT_MACHINE, bot.handle_dice))

    logger.info(f"Бот для канала @{CHANNEL_USERNAME} запущен!")
    print("\n" + "="*60)
    print(f"    STARS REWARDS BOT - КАНАЛ @{CHANNEL_USERNAME}")
    print("="*60)
    print(f"\n[OK] Бот успешно запущен!")
    print(f"[OK] Канал: {CHANNEL_LINK}")
    print(f"[OK] Готов к приёму игр\n")
    print("="*60 + "\n")

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
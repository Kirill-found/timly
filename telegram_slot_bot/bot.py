import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from dotenv import load_dotenv
from database import Database
from game_logic import GameLogic
from achievements import AchievementManager

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация
DATABASE_URL = os.getenv('DATABASE_URL')
db = Database(DATABASE_URL)
game = GameLogic(db)
achievements_manager = AchievementManager(db)

# Инициализация достижений
achievements_manager.initialize_achievements()

# Константы
SPIN_COST = int(os.getenv('SPIN_COST', 35))
ADMIN_IDS = [int(admin_id) for admin_id in os.getenv('ADMIN_IDS', '').split(',') if admin_id]
STARS_CONVERSION_RATE = int(os.getenv('STARS_CONVERSION_RATE', 10))


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user_id in ADMIN_IDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user

    # Проверка на бан
    if db.is_user_banned(user.id):
        await update.message.reply_text("❌ Вы заблокированы в этом боте.")
        return

    # Создаём или получаем пользователя
    db_user = db.get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    welcome_text = f"""
🎰 <b>Добро пожаловать в Lucky Slot Bot!</b>

👋 Привет, {user.first_name}!

💰 Ваш текущий баланс: <b>{db_user.balance} ⭐️</b>

🎮 <b>Как играть:</b>
• Отправь /spin чтобы крутить слот
• Стоимость одного спина: {SPIN_COST} ⭐️

🏆 <b>Таблица выплат:</b>
🍒🍒🍒 = 100 ⭐️
🍋🍋🍋 = 200 ⭐️
🍇🍇🍇 = 350 ⭐️
7️⃣7️⃣7️⃣ = 500 ⭐️ (Джекпот!)

💎 <b>Купить звёзды:</b>
/buy - пополнить баланс через Telegram Stars

📊 <b>Команды:</b>
/balance - проверить баланс
/stats - ваша статистика
/achievements - ваши достижения
/top - топ игроков
/help - справка
    """

    await update.message.reply_text(welcome_text, parse_mode='HTML')


async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /spin - крутим слот"""
    user_id = update.effective_user.id

    # Проверка на бан
    if db.is_user_banned(user_id):
        await update.message.reply_text("❌ Вы заблокированы в этом боте.")
        return

    # Проверяем баланс
    user = db.get_user(user_id)
    if user.balance < SPIN_COST:
        await update.message.reply_text(
            f"❌ Недостаточно звёзд!\n\n"
            f"💰 Ваш баланс: {user.balance} ⭐️\n"
            f"Необходимо: {SPIN_COST} ⭐️\n\n"
            f"Используйте /buy для пополнения баланса"
        )
        return

    # Списываем ставку
    db.update_balance(user_id, -SPIN_COST)

    # Отправляем сообщение о спине
    status_msg = await update.message.reply_text("🎰 Крутим барабаны...")

    # Отправляем слот
    dice_message = await context.bot.send_dice(
        chat_id=update.effective_chat.id,
        emoji="🎰"
    )

    dice_value = dice_message.dice.value
    logger.info(f"User {user_id} spin: dice_value={dice_value}")

    # Проверяем достижения после спина
    unlocked = achievements_manager.check_and_unlock_achievements(user_id, 'spin')

    # Ждём анимацию (слот крутится ~3 секунды)
    await asyncio.sleep(3.5)

    # Проверяем выигрыш
    result = game.check_win(dice_value)

    if result['win']:
        # Выигрыш!
        db.update_balance(user_id, result['payout'])

        # Логируем транзакцию спина
        db.log_transaction(
            user_id=user_id,
            transaction_type='spin',
            amount=-SPIN_COST,
            dice_value=dice_value,
            combination='lose'
        )

        # Логируем выигрыш
        db.log_transaction(
            user_id=user_id,
            transaction_type='win',
            amount=result['payout'],
            dice_value=dice_value,
            combination=result['combination']
        )

        # Проверяем достижения после выигрыша
        win_unlocked = achievements_manager.check_and_unlock_achievements(
            user_id,
            'win',
            win_amount=result['payout'],
            combination=result['combination']
        )
        unlocked.extend(win_unlocked)

        user = db.get_user(user_id)

        response = f"""
🎉 <b>ВЫИГРЫШ!</b> {result['combination']}

💰 Вы выиграли: <b>{result['payout']} ⭐️</b>
💳 Новый баланс: <b>{user.balance} ⭐️</b>
        """
    else:
        # Проигрыш
        db.log_transaction(
            user_id=user_id,
            transaction_type='spin',
            amount=-SPIN_COST,
            dice_value=dice_value,
            combination='lose'
        )

        user = db.get_user(user_id)
        response = f"""
😔 Не повезло в этот раз

💳 Ваш баланс: <b>{user.balance} ⭐️</b>
        """

    # Проверяем баланс для достижений
    balance_unlocked = achievements_manager.check_and_unlock_achievements(user_id, 'balance_check')
    unlocked.extend(balance_unlocked)

    await status_msg.delete()
    await update.message.reply_text(response, parse_mode='HTML')

    # Отправляем уведомления о новых достижениях
    if unlocked:
        for achievement_code in unlocked:
            notification = achievements_manager.format_achievement_notification(achievement_code)
            await update.message.reply_text(notification)


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /balance"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)

    if not user:
        await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
        return

    text = f"""
💰 <b>Ваш баланс</b>

Звёзды: <b>{user.balance} ⭐️</b>

📊 Статистика:
• Всего спинов: {user.total_spins}
• Всего поставлено: {user.total_wagered} ⭐️
• Всего выиграно: {user.total_won} ⭐️
• Самый большой выигрыш: {user.biggest_win} ⭐️

💎 Пополнить баланс: /buy
    """

    await update.message.reply_text(text, parse_mode='HTML')


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stats"""
    user_id = update.effective_user.id
    stats_data = db.get_user_stats(user_id)

    if not stats_data:
        await update.message.reply_text("❌ Статистика не найдена. Используйте /start")
        return

    if stats_data['total_spins'] > 0 and stats_data['total_wagered'] > 0:
        actual_rtp = (stats_data['total_won'] / stats_data['total_wagered']) * 100
    else:
        actual_rtp = 0

    profit_loss = stats_data['profit_loss']
    profit_emoji = "📈" if profit_loss >= 0 else "📉"

    text = f"""
📊 <b>Ваша статистика</b>

🎰 Всего спинов: <b>{stats_data['total_spins']}</b>
💸 Всего поставлено: <b>{stats_data['total_wagered']} ⭐️</b>
🏆 Всего выиграно: <b>{stats_data['total_won']} ⭐️</b>
💎 Самый большой выигрыш: <b>{stats_data['biggest_win']} ⭐️</b>
📈 Ваш RTP: <b>{actual_rtp:.2f}%</b>
💰 Текущий баланс: <b>{stats_data['balance']} ⭐️</b>

{profit_emoji} Прибыль/убыток: <b>{profit_loss:+d} ⭐️</b>

🏅 Достижения разблокировано: <b>{stats_data['achievements']}</b>
    """

    await update.message.reply_text(text, parse_mode='HTML')


async def achievements_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /achievements - показать достижения"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)

    if not user:
        await update.message.reply_text("❌ Пользователь не найден. Используйте /start")
        return

    all_achievements = db.get_all_achievements()
    user_achievement_ids = [ua.achievement_id for ua in db.get_user_achievements(user_id)]

    text = f"🏆 <b>Ваши достижения</b> ({user.achievements_unlocked}/{len(all_achievements)})\n\n"

    unlocked_text = "<b>✅ Разблокированные:</b>\n"
    locked_text = "\n<b>🔒 Заблокированные:</b>\n"

    for achievement in all_achievements:
        if achievement.id in user_achievement_ids:
            unlocked_text += f"{achievement.icon} {achievement.title}\n"
            unlocked_text += f"   <i>{achievement.description}</i>\n"
            unlocked_text += f"   Награда: {achievement.reward} ⭐️\n\n"
        else:
            locked_text += f"🔒 {achievement.title}\n"
            locked_text += f"   <i>{achievement.requirement_description}</i>\n"
            locked_text += f"   Награда: {achievement.reward} ⭐️\n\n"

    text += unlocked_text + locked_text

    await update.message.reply_text(text, parse_mode='HTML')


async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /top - топ игроков"""
    top_users = db.get_top_users(limit=10)

    text = "🏆 <b>Топ-10 игроков по балансу:</b>\n\n"

    medals = ["🥇", "🥈", "🥉"]
    for i, user in enumerate(top_users, 1):
        medal = medals[i - 1] if i <= 3 else f"{i}."
        username = f"@{user.username}" if user.username else user.first_name or "Аноним"
        text += f"{medal} {username}: <b>{user.balance} ⭐️</b>\n"

    await update.message.reply_text(text, parse_mode='HTML')


async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /buy - показать варианты покупки"""
    keyboard = [
        [InlineKeyboardButton("💎 100 звёзд - 10 Stars", callback_data="buy_100")],
        [InlineKeyboardButton("💎 500 звёзд - 50 Stars", callback_data="buy_500")],
        [InlineKeyboardButton("💎 1000 звёзд - 100 Stars", callback_data="buy_1000")],
        [InlineKeyboardButton("💎 5000 звёзд - 500 Stars", callback_data="buy_5000")],
        [InlineKeyboardButton("💎 10000 звёзд - 1000 Stars", callback_data="buy_10000")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = """
💎 <b>Купить игровые звёзды</b>

Выберите пакет для покупки:

<i>Оплата производится через Telegram Stars</i>
    """

    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')


async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки покупки"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    # Определяем пакет
    packages = {
        'buy_100': (100, 10),
        'buy_500': (500, 50),
        'buy_1000': (1000, 100),
        'buy_5000': (5000, 500),
        'buy_10000': (10000, 1000),
    }

    if query.data not in packages:
        return

    game_stars, telegram_stars = packages[query.data]

    # Создаём инвойс
    title = f"{game_stars} игровых звёзд"
    description = f"Покупка {game_stars} игровых звёзд для игры в слот-машину"
    payload = f"stars_{user_id}_{game_stars}_{telegram_stars}"
    currency = "XTR"  # Telegram Stars currency code
    prices = [LabeledPrice(label=f"{game_stars} звёзд", amount=telegram_stars)]

    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title=title,
        description=description,
        payload=payload,
        provider_token="",  # Пустая строка для Telegram Stars
        currency=currency,
        prices=prices
    )


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка pre-checkout запроса"""
    query = update.pre_checkout_query

    # Проверяем payload
    if query.invoice_payload.startswith('stars_'):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Ошибка валидации платежа")


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка успешного платежа"""
    payment = update.message.successful_payment
    user_id = update.effective_user.id

    # Парсим payload
    payload_parts = payment.invoice_payload.split('_')
    game_stars = int(payload_parts[2])
    telegram_stars = int(payload_parts[3])

    logger.info(f"Payment received: user={user_id}, game_stars={game_stars}, telegram_stars={telegram_stars}")

    # Создаём запись о платеже
    payment_record = db.create_payment(
        user_id=user_id,
        telegram_payment_charge_id=payment.telegram_payment_charge_id,
        telegram_stars_amount=telegram_stars,
        game_stars_amount=game_stars,
        provider_payment_charge_id=payment.provider_payment_charge_id
    )

    # Завершаем платёж (начисляем звёзды)
    db.complete_payment(payment_record.id)

    user = db.get_user(user_id)

    await update.message.reply_text(
        f"✅ <b>Платёж успешно завершён!</b>\n\n"
        f"💎 Вы получили: <b>{game_stars} ⭐️</b>\n"
        f"💰 Новый баланс: <b>{user.balance} ⭐️</b>\n\n"
        f"Спасибо за покупку! 🎰",
        parse_mode='HTML'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    text = """
🎰 <b>Lucky Slot Bot - Справка</b>

📋 <b>Доступные команды:</b>
/start - начать игру
/spin - крутить слот (стоит 35 ⭐️)
/balance - проверить баланс
/stats - ваша статистика
/achievements - ваши достижения
/top - топ игроков
/buy - купить звёзды
/help - эта справка

🎮 <b>Как играть:</b>
1. Используй /spin для вращения слота
2. Собирай выигрышные комбинации
3. Получай звёзды за выигрыши
4. Разблокируй достижения

🏆 <b>Таблица выплат:</b>
🍒🍒🍒 = 100 ⭐️
🍋🍋🍋 = 200 ⭐️
🍇🍇🍇 = 350 ⭐️
7️⃣7️⃣7️⃣ = 500 ⭐️ (Джекпот!)

💎 <b>Покупка звёзд:</b>
Используй /buy для пополнения баланса через Telegram Stars

💡 <b>Совет:</b> Управляй банкроллом разумно!
    """

    await update.message.reply_text(text, parse_mode='HTML')


# ==================== ADMIN COMMANDS ====================

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /adminstats - глобальная статистика (только для админов)"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ У вас нет доступа к этой команде")
        return

    stats = db.get_global_stats()

    text = f"""
📊 <b>Глобальная статистика</b>

👥 Всего пользователей: <b>{stats['total_users']}</b>
🟢 Активные (24ч): <b>{stats['active_users']}</b>
🆕 Новые (24ч): <b>{stats['new_users']}</b>

🎰 Всего спинов: <b>{stats['total_spins']}</b>
💸 Всего поставлено: <b>{stats['total_wagered']} ⭐️</b>
🏆 Всего выплачено: <b>{stats['total_won']} ⭐️</b>
💰 Общий баланс игроков: <b>{stats['total_balance']} ⭐️</b>

📈 Актуальный RTP: <b>{stats['actual_rtp']:.2f}%</b>
💹 Прибыль "казино": <b>{stats['house_profit']} ⭐️</b>

💳 <b>Платежи:</b>
• Всего покупок: <b>{stats['total_purchases']}</b>
• Получено Telegram Stars: <b>{stats['total_telegram_stars_received']}</b>
• Продано игровых звёзд: <b>{stats['total_game_stars_sold']} ⭐️</b>
    """

    await update.message.reply_text(text, parse_mode='HTML')


async def admin_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /ban - заблокировать пользователя"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ У вас нет доступа к этой команде")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Использование: /ban <user_id> [причина]")
        return

    try:
        target_user_id = int(context.args[0])
        reason = ' '.join(context.args[1:]) if len(context.args) > 1 else "Не указана"

        db.ban_user(target_user_id, reason)
        await update.message.reply_text(f"✅ Пользователь {target_user_id} заблокирован\nПричина: {reason}")
    except ValueError:
        await update.message.reply_text("❌ Неверный ID пользователя")


async def admin_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /unban - разблокировать пользователя"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ У вас нет доступа к этой команде")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Использование: /unban <user_id>")
        return

    try:
        target_user_id = int(context.args[0])
        db.unban_user(target_user_id)
        await update.message.reply_text(f"✅ Пользователь {target_user_id} разблокирован")
    except ValueError:
        await update.message.reply_text("❌ Неверный ID пользователя")


async def admin_give_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /givestars - выдать звёзды пользователю"""
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("❌ У вас нет доступа к этой команде")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Использование: /givestars <user_id> <amount>")
        return

    try:
        target_user_id = int(context.args[0])
        amount = int(context.args[1])

        user = db.get_user(target_user_id)
        if not user:
            await update.message.reply_text(f"❌ Пользователь {target_user_id} не найден")
            return

        db.update_balance(target_user_id, amount)
        db.log_transaction(
            user_id=target_user_id,
            transaction_type='bonus',
            amount=amount,
            description=f"Бонус от администратора"
        )

        await update.message.reply_text(
            f"✅ Пользователю {target_user_id} выдано {amount} ⭐️\n"
            f"Новый баланс: {user.balance + amount} ⭐️"
        )
    except ValueError:
        await update.message.reply_text("❌ Неверные параметры")


def main():
    """Запуск бота"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return

    # Создаём приложение
    application = Application.builder().token(token).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("spin", spin))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("achievements", achievements_command))
    application.add_handler(CommandHandler("top", top))
    application.add_handler(CommandHandler("buy", buy_command))
    application.add_handler(CommandHandler("help", help_command))

    # Админ команды
    application.add_handler(CommandHandler("adminstats", admin_stats))
    application.add_handler(CommandHandler("ban", admin_ban))
    application.add_handler(CommandHandler("unban", admin_unban))
    application.add_handler(CommandHandler("givestars", admin_give_stars))

    # Обработчики платежей
    application.add_handler(CallbackQueryHandler(buy_callback, pattern='^buy_'))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # Запускаем бота
    logger.info("🎰 Lucky Slot Bot запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

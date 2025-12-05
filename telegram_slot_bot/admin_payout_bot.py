"""
Админ-бот для управления выплатами

Функции:
- Уведомляет администратора о новых выигрышах
- Показывает список ожидающих выплат
- Позволяет отметить выплату как оплаченную
- Показывает статистику
"""

import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import BadRequest

from database import Database

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
ADMIN_ID = int(os.getenv('ADMIN_IDS', '0').split(',')[0])  # Первый админ из списка

# Инициализация базы данных
db = Database(DATABASE_URL)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Access denied. Admins only.")
        return

    await update.message.reply_text(
        "🤖 Админ-бот управления выплатами\n\n"
        "Команды:\n"
        "/pending - Показать ожидающие выплаты\n"
        "/stats - Статистика выплат\n"
        "/notify - Включить уведомления о новых выигрышах"
    )


async def pending_payouts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список ожидающих выплат"""
    if update.effective_user.id != ADMIN_ID:
        return

    payouts = db.get_pending_payouts(status='pending')

    if not payouts:
        await update.message.reply_text("✅ Нет ожидающих выплат!")
        return

    message = "💰 <b>Ожидающие выплаты:</b>\n\n"

    for payout in payouts[:10]:  # Показываем первые 10
        username = f"@{payout.username}" if payout.username else f"ID: {payout.user_id}"
        created = payout.created_at.strftime("%d.%m %H:%M")

        message += (
            f"🎫 <b>ID #{payout.id}</b>\n"
            f"👤 {username}\n"
            f"💵 <b>{payout.amount} ⭐</b>\n"
            f"🎰 {payout.combination or 'N/A'}\n"
            f"📅 {created}\n"
            f"─────────────\n"
        )

        # Кнопки для каждой выплаты
        keyboard = [
            [
                InlineKeyboardButton("✅ Оплачено", callback_data=f"paid_{payout.id}"),
                InlineKeyboardButton("❌ Ошибка", callback_data=f"failed_{payout.id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            await update.message.reply_text(
                message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        except BadRequest:
            pass

        message = ""  # Сброс для следующей порции

    if len(payouts) > 10:
        await update.message.reply_text(f"... и ещё {len(payouts) - 10} выплат")


async def payout_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику выплат"""
    if update.effective_user.id != ADMIN_ID:
        return

    stats = db.get_payout_stats()

    message = f"""
📊 <b>Статистика выплат</b>

⏳ <b>Ожидают оплаты:</b>
   Количество: {stats['pending_count']}
   Сумма: {stats['pending_amount']} ⭐

✅ <b>Оплачено:</b>
   Количество: {stats['paid_count']}
   Сумма: {stats['paid_amount']} ⭐

💰 <b>Общая задолженность:</b> {stats['pending_amount']} ⭐
"""

    await update.message.reply_text(message, parse_mode='HTML')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    data = query.data
    action, payout_id = data.split('_')
    payout_id = int(payout_id)

    if action == 'paid':
        db.mark_payout_paid(payout_id, admin_note=f"Marked by admin at {datetime.now()}")
        await query.edit_message_text(
            f"✅ Выплата #{payout_id} отмечена как оплаченная",
            parse_mode='HTML'
        )
        logger.info(f"Admin marked payout {payout_id} as paid")

    elif action == 'failed':
        db.mark_payout_failed(payout_id, error="Marked as failed by admin")
        await query.edit_message_text(
            f"❌ Выплата #{payout_id} отмечена как неудачная",
            parse_mode='HTML'
        )
        logger.info(f"Admin marked payout {payout_id} as failed")


async def check_new_payouts(context: ContextTypes.DEFAULT_TYPE):
    """
    Периодическая проверка новых выплат (каждые 5 минут)
    Отправляет уведомление админу о новых выигрышах
    """
    # Получаем выплаты созданные за последние 5 минут
    payouts = db.get_pending_payouts(status='pending')

    for payout in payouts:
        # Проверяем что выплата новая (создана менее 6 минут назад)
        time_diff = datetime.utcnow() - payout.created_at
        if time_diff.total_seconds() < 360:  # 6 минут
            username = f"@{payout.username}" if payout.username else f"ID: {payout.user_id}"

            message = (
                f"🔔 <b>Новый выигрыш!</b>\n\n"
                f"👤 {username}\n"
                f"💰 <b>{payout.amount} ⭐</b>\n"
                f"🎰 {payout.combination}\n"
                f"📅 {payout.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
                f"ID выплаты: #{payout.id}"
            )

            keyboard = [
                [
                    InlineKeyboardButton("✅ Оплачено", callback_data=f"paid_{payout.id}"),
                    InlineKeyboardButton("❌ Ошибка", callback_data=f"failed_{payout.id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            try:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=message,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                logger.info(f"Sent notification about payout {payout.id} to admin")
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")


def main():
    """Запуск бота"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found!")
        return

    if ADMIN_ID == 0:
        logger.error("ADMIN_IDS not configured!")
        return

    # Создаём приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pending", pending_payouts))
    application.add_handler(CommandHandler("stats", payout_stats))

    # Обработка кнопок
    application.add_handler(CallbackQueryHandler(button_callback))

    # Периодическая проверка новых выплат (каждые 5 минут)
    job_queue = application.job_queue
    job_queue.run_repeating(check_new_payouts, interval=300, first=10)

    logger.info("🤖 Admin Payout Bot запущен!")
    logger.info(f"Admin ID: {ADMIN_ID}")

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

"""
Модуль для тестирования Telegram Dice API и определения соответствия
dice_value реальным комбинациям слот-машины

Использование:
1. Создайте тестового бота
2. Запустите этот скрипт
3. Отправьте команду /test в бот
4. Бот будет отправлять спины и записывать результаты
5. После 100+ спинов используйте /analyze для анализа

ВАЖНО: Вручную записывайте визуальные результаты!
"""

import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from database import Database
import asyncio

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')
db = Database(DATABASE_URL)

# Счётчик тестовых спинов
test_counter = 0


async def test_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /test - тестирование dice"""
    global test_counter

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Количество спинов для теста
    num_spins = 10
    if context.args and context.args[0].isdigit():
        num_spins = int(context.args[0])

    await update.message.reply_text(
        f"🎰 Начинаю тестирование...\n"
        f"Количество спинов: {num_spins}\n\n"
        f"⚠️ ВНИМАНИЕ: Записывайте визуальные результаты вручную!"
    )

    results = []

    for i in range(num_spins):
        # Отправляем dice
        dice_message = await context.bot.send_dice(
            chat_id=chat_id,
            emoji="🎰"
        )

        dice_value = dice_message.dice.value
        test_counter += 1

        # Записываем в БД
        db.record_dice_value(dice_value)

        results.append(dice_value)

        # Отправляем информацию о результате
        await update.message.reply_text(
            f"Спин #{i + 1}: dice_value = {dice_value}"
        )

        logger.info(f"Test spin #{test_counter}: dice_value={dice_value}")

        # Пауза между спинами
        await asyncio.sleep(4)

    # Статистика
    unique_values = set(results)
    value_counts = {val: results.count(val) for val in unique_values}

    stats_text = f"""
✅ Тестирование завершено!

Всего спинов: {num_spins}
Уникальных значений: {len(unique_values)}

Распределение:
"""

    for value in sorted(value_counts.keys()):
        count = value_counts[value]
        percentage = (count / num_spins) * 100
        stats_text += f"\n{value}: {count} раз ({percentage:.1f}%)"

    stats_text += "\n\nИспользуйте /analyze для полного анализа"

    await update.message.reply_text(stats_text)


async def analyze_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /analyze - анализ собранной статистики"""
    dice_stats = db.get_dice_statistics()

    if not dice_stats:
        await update.message.reply_text("❌ Нет данных для анализа. Сначала используйте /test")
        return

    total_spins = sum(stat.occurrence_count for stat in dice_stats)

    text = f"""
📊 Анализ Telegram Dice API

Всего записано спинов: {total_spins}
Уникальных значений: {len(dice_stats)}

━━━━━━━━━━━━━━━━━━━━
Распределение (топ-20):
━━━━━━━━━━━━━━━━━━━━
"""

    # Сортируем по частоте
    sorted_stats = sorted(dice_stats, key=lambda x: x.occurrence_count, reverse=True)[:20]

    for stat in sorted_stats:
        probability = (stat.occurrence_count / total_spins) * 100
        combo_info = f" [{stat.combination}]" if stat.combination else ""
        win_mark = " 🏆" if stat.is_win else ""

        text += f"\n{stat.dice_value}{combo_info}{win_mark}"
        text += f"\n  {stat.occurrence_count} раз ({probability:.2f}%)"
        text += f"\n  Последний: {stat.last_seen.strftime('%Y-%m-%d %H:%M')}\n"

    text += "\n━━━━━━━━━━━━━━━━━━━━"
    text += "\n\nВыигрышные комбинации:"

    win_stats = [s for s in dice_stats if s.is_win]
    if win_stats:
        for stat in win_stats:
            probability = (stat.occurrence_count / total_spins) * 100
            text += f"\n{stat.combination} (value={stat.dice_value})"
            text += f"\n  Вероятность: {probability:.4f}%"
            text += f"\n  Множитель: {stat.payout_multiplier:.2f}x\n"
    else:
        text += "\n⚠️ Выигрышные комбинации не определены"
        text += "\nОбновите DICE_TO_COMBO в game_logic.py"

    # Расчёт теоретического RTP
    if win_stats:
        expected_return = sum(
            (stat.occurrence_count / total_spins) * stat.payout_multiplier * 35
            for stat in win_stats
        )
        rtp = (expected_return / 35) * 100

        text += f"\n\n📈 Теоретический RTP: {rtp:.2f}%"

    await update.message.reply_text(text)


async def reset_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /resetstats - сброс статистики тестирования"""
    global test_counter

    user_id = update.effective_user.id

    # Только для админов или в режиме тестирования
    confirmation = context.args and context.args[0] == "confirm"

    if not confirmation:
        await update.message.reply_text(
            "⚠️ Это удалит ВСЕ данные о dice_value!\n"
            "Для подтверждения используйте: /resetstats confirm"
        )
        return

    # Удаляем все записи
    from models import DiceValueMapping
    db.session.query(DiceValueMapping).delete()
    db.session.commit()

    test_counter = 0

    await update.message.reply_text("✅ Статистика тестирования сброшена")


async def export_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /export - экспорт статистики в CSV"""
    dice_stats = db.get_dice_statistics()

    if not dice_stats:
        await update.message.reply_text("❌ Нет данных для экспорта")
        return

    # Создаём CSV
    csv_content = "dice_value,combination,is_win,payout_multiplier,occurrence_count,last_seen\n"

    for stat in sorted(dice_stats, key=lambda x: x.dice_value):
        csv_content += f"{stat.dice_value},"
        csv_content += f"{stat.combination or ''},"
        csv_content += f"{stat.is_win},"
        csv_content += f"{stat.payout_multiplier},"
        csv_content += f"{stat.occurrence_count},"
        csv_content += f"{stat.last_seen}\n"

    # Сохраняем в файл
    filename = f"dice_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(csv_content)

    # Отправляем файл
    await update.message.reply_document(
        document=open(filename, 'rb'),
        filename=filename,
        caption=f"📊 Статистика dice_value\n{len(dice_stats)} уникальных значений"
    )

    logger.info(f"Stats exported to {filename}")


def main():
    """Запуск тестового бота"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found!")
        return

    application = Application.builder().token(token).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("test", test_dice))
    application.add_handler(CommandHandler("analyze", analyze_dice))
    application.add_handler(CommandHandler("resetstats", reset_stats))
    application.add_handler(CommandHandler("export", export_stats))

    logger.info("🧪 Dice Tester Bot запущен!")
    logger.info("Доступные команды:")
    logger.info("  /test [num_spins] - тестирование (по умолчанию 10)")
    logger.info("  /analyze - анализ статистики")
    logger.info("  /export - экспорт в CSV")
    logger.info("  /resetstats confirm - сброс статистики")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

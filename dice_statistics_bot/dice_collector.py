"""
Бот для сбора статистики по dice emoji
Отправляет много бросков dice и записывает результаты
"""

import asyncio
import os
import csv
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import DiceEmoji
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', '517682186'))
ROLLS_COUNT = int(os.getenv('ROLLS_COUNT', '1000'))

class DiceStatisticsCollector:
    """Сборщик статистики по dice"""

    def __init__(self):
        self.results = []
        self.csv_filename = f"dice_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    async def collect_statistics(self, app, chat_id):
        """Собирает статистику, отправляя dice"""

        print("\n" + "="*60)
        print(f"    НАЧАЛО СБОРА СТАТИСТИКИ")
        print("="*60)
        print(f"Количество бросков: {ROLLS_COUNT}")
        print(f"Результаты будут сохранены в: {self.csv_filename}\n")

        # Открываем CSV файл для записи
        with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Roll Number', 'Dice Value', 'Timestamp'])

            for i in range(1, ROLLS_COUNT + 1):
                try:
                    # Отправляем dice
                    message = await app.bot.send_dice(
                        chat_id=chat_id,
                        emoji=DiceEmoji.SLOT_MACHINE
                    )

                    dice_value = message.dice.value
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Сохраняем результат
                    self.results.append(dice_value)
                    writer.writerow([i, dice_value, timestamp])

                    # Выводим прогресс
                    if i % 50 == 0:
                        print(f"Прогресс: {i}/{ROLLS_COUNT} ({i*100//ROLLS_COUNT}%)")

                    # Небольшая пауза чтобы не словить flood limit
                    await asyncio.sleep(0.5)

                except Exception as e:
                    print(f"Ошибка на броске {i}: {e}")
                    await asyncio.sleep(2)
                    continue

        print(f"\n[OK] Все {ROLLS_COUNT} бросков завершены!")
        print(f"[OK] Данные сохранены в {self.csv_filename}\n")

        # Анализируем результаты
        await self.analyze_results(app, chat_id)

    async def analyze_results(self, app, chat_id):
        """Анализирует собранную статистику"""

        print("="*60)
        print("    АНАЛИЗ РЕЗУЛЬТАТОВ")
        print("="*60 + "\n")

        # Подсчитываем частоты
        counter = Counter(self.results)
        total = len(self.results)

        # Сортируем по значению
        sorted_results = sorted(counter.items())

        # Создаем отчет
        report_lines = []
        report_lines.append("=== СТАТИСТИКА DICE ===\n")
        report_lines.append(f"Всего бросков: {total}\n")
        report_lines.append(f"Уникальных значений: {len(counter)}\n\n")
        report_lines.append("РАСПРЕДЕЛЕНИЕ ЗНАЧЕНИЙ:\n")
        report_lines.append("-" * 40 + "\n")

        # Выводим все значения
        for value, count in sorted_results:
            percentage = (count / total) * 100
            report_lines.append(f"Value {value:2d}: {count:4d} раз ({percentage:5.2f}%)\n")
            print(f"Value {value:2d}: {count:4d} раз ({percentage:5.2f}%)")

        # Находим наиболее частые значения
        most_common = counter.most_common(10)
        report_lines.append("\n" + "="*40 + "\n")
        report_lines.append("ТОП-10 ЧАСТЫХ ЗНАЧЕНИЙ:\n")
        report_lines.append("-" * 40 + "\n")

        print("\nТоп-10 самых частых значений:")
        for value, count in most_common:
            percentage = (count / total) * 100
            report_lines.append(f"{value}: {count} раз ({percentage:.2f}%)\n")
            print(f"  {value}: {count} раз ({percentage:.2f}%)")

        # Сохраняем отчет
        report_filename = f"dice_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.writelines(report_lines)

        print(f"\n[OK] Отчет сохранен в {report_filename}")

        # Отправляем отчет в Telegram
        try:
            report_message = ''.join(report_lines[:30])  # Первые 30 строк
            if len(report_message) > 4000:
                report_message = report_message[:4000] + "...\n\nПолный отчет в файле"

            await app.bot.send_message(
                chat_id=chat_id,
                text=f"```\n{report_message}\n```",
                parse_mode='Markdown'
            )

            # Отправляем файлы
            with open(self.csv_filename, 'rb') as f:
                await app.bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    caption="CSV с данными всех бросков"
                )

            with open(report_filename, 'rb') as f:
                await app.bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    caption="Полный отчет по статистике"
                )

            print("[OK] Отчет отправлен в Telegram")

        except Exception as e:
            print(f"[ERROR] Ошибка отправки отчета: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        "Бот для сбора статистики dice\n\n"
        "Команды:\n"
        "/collect - начать сбор статистики\n"
        "/help - помощь"
    )

async def collect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /collect - начать сбор"""
    chat_id = update.effective_chat.id

    await update.message.reply_text(
        f"Начинаю сбор статистики...\n"
        f"Буду отправлять {ROLLS_COUNT} dice\n"
        f"Это займет примерно {ROLLS_COUNT * 0.5 / 60:.1f} минут"
    )

    collector = DiceStatisticsCollector()

    try:
        await collector.collect_statistics(context.application, chat_id)
        await update.message.reply_text("Сбор статистики завершен!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при сборе: {e}")
        print(f"[ERROR] {e}")

def main():
    """Запуск бота"""

    print("\n" + "="*60)
    print("    БОТ ДЛЯ СБОРА СТАТИСТИКИ DICE")
    print("="*60)
    print(f"\nНастройки:")
    print(f"  - Бросков для сбора: {ROLLS_COUNT}")
    print(f"  - Admin chat ID: {ADMIN_CHAT_ID}")
    print("\n[!] Напишите боту /start чтобы начать")
    print("[!] Затем отправьте /collect для сбора статистики\n")
    print("="*60 + "\n")

    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("collect", collect_command))

    # Запускаем
    print("[OK] Бот запущен и ожидает команд...\n")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

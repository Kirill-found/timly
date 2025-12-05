"""
Упрощенная версия бота для сбора статистики dice
"""

import asyncio
import os
import csv
from datetime import datetime
from telegram import Bot
from telegram.constants import DiceEmoji
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', '517682186'))
ROLLS_COUNT = int(os.getenv('ROLLS_COUNT', '1000'))

async def collect_statistics():
    """Собирает статистику dice"""

    bot = Bot(token=BOT_TOKEN)

    # Проверяем подключение
    me = await bot.get_me()
    print(f"\nBOT: @{me.username}")
    print(f"Chat ID: {ADMIN_CHAT_ID}")
    print(f"Rolls count: {ROLLS_COUNT}\n")

    results = []
    csv_filename = f"dice_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    print(f"Saving to: {csv_filename}\n")

    # Открываем CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Roll', 'Value', 'Time'])

        for i in range(1, ROLLS_COUNT + 1):
            try:
                # Отправляем dice
                message = await bot.send_dice(
                    chat_id=ADMIN_CHAT_ID,
                    emoji=DiceEmoji.SLOT_MACHINE
                )

                value = message.dice.value
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                results.append(value)
                writer.writerow([i, value, timestamp])

                # Прогресс
                if i % 50 == 0:
                    print(f"Progress: {i}/{ROLLS_COUNT} ({i*100//ROLLS_COUNT}%)")

                # Пауза
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"Error on roll {i}: {e}")
                await asyncio.sleep(2)

    print(f"\nDone! {len(results)} rolls collected")

    # Анализ
    counter = Counter(results)
    total = len(results)

    print("\nSTATISTICS:")
    print("="*50)

    report_lines = []
    report_lines.append("DICE STATISTICS\n")
    report_lines.append(f"Total rolls: {total}\n")
    report_lines.append(f"Unique values: {len(counter)}\n\n")

    # Сортируем
    for value, count in sorted(counter.items()):
        percentage = (count / total) * 100
        line = f"Value {value:2d}: {count:4d} times ({percentage:5.2f}%)"
        print(line)
        report_lines.append(line + "\n")

    # Топ-10
    print("\nTOP-10:")
    report_lines.append("\nTOP-10:\n")
    for value, count in counter.most_common(10):
        percentage = (count / total) * 100
        line = f"  {value}: {count} times ({percentage:.2f}%)"
        print(line)
        report_lines.append(line + "\n")

    # Сохраняем отчет
    report_filename = f"dice_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.writelines(report_lines)

    print(f"\nReport saved: {report_filename}")

    # Отправляем в Telegram
    try:
        report_text = ''.join(report_lines[:25])
        if len(report_text) > 4000:
            report_text = report_text[:4000]

        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"```\n{report_text}\n```",
            parse_mode='Markdown'
        )

        # Файлы
        with open(csv_filename, 'rb') as f:
            await bot.send_document(
                chat_id=ADMIN_CHAT_ID,
                document=f,
                caption="CSV data"
            )

        with open(report_filename, 'rb') as f:
            await bot.send_document(
                chat_id=ADMIN_CHAT_ID,
                document=f,
                caption="Full report"
            )

        print("Report sent to Telegram!")

    except Exception as e:
        print(f"Error sending report: {e}")

    await bot.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("    DICE STATISTICS COLLECTOR")
    print("="*60)
    print("\nStarting collection...")

    asyncio.run(collect_statistics())

    print("\n" + "="*60)
    print("    FINISHED")
    print("="*60 + "\n")

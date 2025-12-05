"""
Прямой сборщик статистики через requests
Использует простые HTTP запросы к Telegram Bot API
"""

import time
import csv
import requests
from datetime import datetime
from collections import Counter
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', '517682186'))
ROLLS_COUNT = int(os.getenv('ROLLS_COUNT', '1000'))

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_dice(chat_id):
    """Отправляет dice и возвращает значение"""
    url = f"{API_URL}/sendDice"
    data = {
        "chat_id": chat_id,
        "emoji": "\ud83c\udfb0"  # Slot machine emoji
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        if result['ok']:
            return result['result']['dice']['value']
    return None

def send_message(chat_id, text):
    """Отправляет сообщение"""
    url = f"{API_URL}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=data)

def send_document(chat_id, file_path, caption=""):
    """Отправляет файл"""
    url = f"{API_URL}/sendDocument"
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': chat_id, 'caption': caption}
        requests.post(url, data=data, files=files)

def main():
    print("\n" + "="*60)
    print("    DICE STATISTICS COLLECTOR")
    print("="*60)
    print(f"\nBot Token: {BOT_TOKEN[:20]}...")
    print(f"Chat ID: {ADMIN_CHAT_ID}")
    print(f"Target rolls: {ROLLS_COUNT}\n")

    results = []
    csv_filename = f"dice_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    print(f"Saving to: {csv_filename}")
    print("Starting collection...\n")

    # Уведомляем начало
    send_message(ADMIN_CHAT_ID, f"Starting collection of {ROLLS_COUNT} dice rolls!")

    # Открываем CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Roll', 'Value', 'Time'])

        for i in range(1, ROLLS_COUNT + 1):
            try:
                # Отправляем dice
                value = send_dice(ADMIN_CHAT_ID)

                if value is not None:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    results.append(value)
                    writer.writerow([i, value, timestamp])

                    # Прогресс каждые 50 бросков
                    if i % 50 == 0:
                        progress_pct = (i * 100) // ROLLS_COUNT
                        print(f"Progress: {i}/{ROLLS_COUNT} ({progress_pct}%)")
                        send_message(ADMIN_CHAT_ID, f"Progress: {i}/{ROLLS_COUNT} ({progress_pct}%)")

                    # Пауза
                    time.sleep(0.5)
                else:
                    print(f"Error on roll {i}: No value returned")
                    time.sleep(2)

            except Exception as e:
                print(f"Error on roll {i}: {e}")
                time.sleep(2)

    print(f"\nDone! {len(results)} rolls collected")
    send_message(ADMIN_CHAT_ID, f"Collection complete! {len(results)} rolls")

    # Анализ
    print("\n" + "="*60)
    print("    ANALYSIS")
    print("="*60 + "\n")

    counter = Counter(results)
    total = len(results)

    report_lines = []
    report_lines.append("=== DICE STATISTICS ===\n\n")
    report_lines.append(f"Total rolls: {total}\n")
    report_lines.append(f"Unique values: {len(counter)}\n\n")
    report_lines.append("DISTRIBUTION:\n")
    report_lines.append("-" * 40 + "\n")

    # Все значения
    for value, count in sorted(counter.items()):
        percentage = (count / total) * 100
        line = f"Value {value:2d}: {count:4d} times ({percentage:5.2f}%)"
        print(line)
        report_lines.append(line + "\n")

    # Топ-10
    print("\nTOP-10 MOST COMMON:")
    report_lines.append("\n" + "="*40 + "\n")
    report_lines.append("TOP-10 MOST COMMON:\n")
    report_lines.append("-" * 40 + "\n")

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
    print("\nSending results to Telegram...")

    try:
        # Отправляем краткий отчет
        report_text = ''.join(report_lines[:30])
        if len(report_text) > 4000:
            report_text = report_text[:4000] + "...\n\n(Full report in file)"

        send_message(ADMIN_CHAT_ID, f"```\n{report_text}\n```")

        # Отправляем файлы
        send_document(ADMIN_CHAT_ID, csv_filename, "CSV data with all rolls")
        send_document(ADMIN_CHAT_ID, report_filename, "Full analysis report")

        print("Results sent to Telegram!")

    except Exception as e:
        print(f"Error sending results: {e}")

    print("\n" + "="*60)
    print("    FINISHED")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

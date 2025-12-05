"""
Сборщик статистики с выводом в реальном времени
"""

import time
import csv
import requests
import sys
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
        "emoji": "\ud83c\udfb0"
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
        "text": text
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
    print(f"\nChat ID: {ADMIN_CHAT_ID}")
    print(f"Target rolls: {ROLLS_COUNT}\n")
    sys.stdout.flush()

    results = []
    csv_filename = f"dice_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    print(f"Saving to: {csv_filename}")
    print("Starting...\n")
    sys.stdout.flush()

    # Открываем CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Roll', 'Value', 'Time'])
        csvfile.flush()

        for i in range(1, ROLLS_COUNT + 1):
            try:
                # Отправляем dice
                value = send_dice(ADMIN_CHAT_ID)

                if value is not None:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    results.append(value)
                    writer.writerow([i, value, timestamp])
                    csvfile.flush()

                    # Выводим каждый бросок
                    print(f"[{i:4d}] Value: {value:2d} | Time: {timestamp}")
                    sys.stdout.flush()

                    # Промежуточная статистика каждые 100
                    if i % 100 == 0:
                        counter = Counter(results)
                        top3 = counter.most_common(3)
                        print(f"\n--- Progress: {i}/{ROLLS_COUNT} ---")
                        print("Top 3:")
                        for val, cnt in top3:
                            pct = (cnt/len(results))*100
                            print(f"  Value {val}: {cnt} ({pct:.1f}%)")
                        print("")
                        sys.stdout.flush()

                        send_message(ADMIN_CHAT_ID, f"Progress: {i}/{ROLLS_COUNT}")

                    time.sleep(0.5)
                else:
                    print(f"[ERROR] Roll {i}: No value")
                    sys.stdout.flush()
                    time.sleep(2)

            except Exception as e:
                print(f"[ERROR] Roll {i}: {e}")
                sys.stdout.flush()
                time.sleep(2)

    print(f"\n{'='*60}")
    print(f"DONE! Collected {len(results)} rolls")
    print(f"{'='*60}\n")
    sys.stdout.flush()

    # Финальный анализ
    counter = Counter(results)
    total = len(results)

    print("FINAL STATISTICS:")
    print("-" * 60)

    report_lines = []
    report_lines.append("=== DICE STATISTICS ===\n\n")
    report_lines.append(f"Total: {total}\n")
    report_lines.append(f"Unique values: {len(counter)}\n\n")

    for value, count in sorted(counter.items()):
        percentage = (count / total) * 100
        line = f"Value {value:2d}: {count:4d} ({percentage:5.2f}%)"
        print(line)
        report_lines.append(line + "\n")
        sys.stdout.flush()

    print("\nTOP-10:")
    report_lines.append("\nTOP-10:\n")
    for value, count in counter.most_common(10):
        percentage = (count / total) * 100
        line = f"  {value}: {count} ({percentage:.2f}%)"
        print(line)
        report_lines.append(line + "\n")
        sys.stdout.flush()

    # Сохраняем отчет
    report_filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.writelines(report_lines)

    print(f"\nReport: {report_filename}")
    print("\nSending to Telegram...")
    sys.stdout.flush()

    # Отправляем
    try:
        report_text = ''.join(report_lines)
        if len(report_text) > 4000:
            report_text = report_text[:4000]

        send_message(ADMIN_CHAT_ID, f"```\n{report_text}\n```")
        send_document(ADMIN_CHAT_ID, csv_filename, "CSV data")
        send_document(ADMIN_CHAT_ID, report_filename, "Full report")

        print("Sent!")
    except Exception as e:
        print(f"Error: {e}")

    sys.stdout.flush()
    print("\n" + "="*60)
    print("    FINISHED")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

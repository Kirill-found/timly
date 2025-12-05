"""
Отправляет тестовые dice с известными значениями для маппинга
Использует Pyrogram для отправки dice с конкретными значениями
"""

import os
import time
from dotenv import load_dotenv
import requests

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID', '517682186'))
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    """Отправляет сообщение"""
    url = f"{API_URL}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=data)

def send_dice(chat_id):
    """Отправляет dice"""
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

def main():
    print("\n" + "="*60)
    print("    ТЕСТОВАЯ ОТПРАВКА ДЛЯ МАППИНГА")
    print("="*60 + "\n")

    # Важные значения для проверки
    important_values = [1, 22, 43, 64, 2, 15, 42, 50, 9, 48, 54, 12, 62]

    send_message(ADMIN_CHAT_ID,
        "🎯 Отправляю тестовые dice для определения маппинга значений!\n"
        "Посмотрите какие символы выпадают и запомните."
    )

    print(f"Отправляю {len(important_values)} тестовых dice...")
    print("Важные значения из статистики:")
    print(f"  {important_values}\n")

    # Отправляем по несколько dice и ждем чтобы успеть увидеть
    for i in range(30):  # Отправим 30 dice
        value = send_dice(ADMIN_CHAT_ID)
        if value:
            print(f"[{i+1:2d}] Отправлен dice, значение: {value}")
            if value in important_values:
                print(f"     ⭐ ЭТО ВАЖНОЕ ЗНАЧЕНИЕ! Запомните что видите!")
                send_message(ADMIN_CHAT_ID, f"⭐ Value {value} - запомните символы!")
        time.sleep(2)  # Пауза 2 секунды чтобы успеть посмотреть

    print("\n" + "="*60)
    print("Готово! Теперь посмотрите на dice выше и определите паттерн")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

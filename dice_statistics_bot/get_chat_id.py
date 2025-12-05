"""
Простой скрипт для получения вашего chat_id
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

print("\n" + "="*60)
print("    ПОЛУЧЕНИЕ CHAT_ID")
print("="*60)
print("\n1. Напишите боту любое сообщение в Telegram")
print("2. Затем запустите этот скрипт\n")

input("Нажмите Enter когда напишете боту сообщение...")

# Получаем обновления
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    if data['result']:
        for update in data['result']:
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                username = update['message']['from'].get('username', 'NoUsername')
                first_name = update['message']['from'].get('first_name', '')

                print(f"\n[OK] Найден чат:")
                print(f"  Chat ID: {chat_id}")
                print(f"  Username: @{username}")
                print(f"  Имя: {first_name}")
                print(f"\nДобавьте в .env файл:")
                print(f"ADMIN_CHAT_ID={chat_id}")
                print("\n")
    else:
        print("\n[!] Сообщений не найдено")
        print("[!] Убедитесь что вы отправили сообщение боту\n")
else:
    print(f"\n[ERROR] Ошибка API: {response.status_code}\n")

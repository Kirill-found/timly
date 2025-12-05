"""
Анализирует dice которые уже отправлены боту через getUpdates
"""

import os
import requests
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

print("\n" + "="*60)
print("    АНАЛИЗ ОТПРАВЛЕННЫХ DICE")
print("="*60 + "\n")

# Получаем обновления
response = requests.get(f"{API_URL}/getUpdates")

if response.status_code == 200:
    data = response.json()

    if data['ok']:
        updates = data['result']

        # Собираем все dice
        dice_values = []

        for update in updates:
            if 'message' in update and 'dice' in update['message']:
                dice = update['message']['dice']
                if dice['emoji'] == '🎰':
                    dice_values.append(dice['value'])

        if dice_values:
            print(f"Найдено dice: {len(dice_values)}\n")

            # Анализ
            counter = Counter(dice_values)
            total = len(dice_values)

            print("СТАТИСТИКА ПО ЗНАЧЕНИЯМ:")
            print("-" * 50)

            for value, count in sorted(counter.items()):
                percentage = (count / total) * 100
                bar = "█" * int(percentage / 2)
                print(f"Value {value:2d}: {count:4d} раз ({percentage:5.2f}%) {bar}")

            print("\n" + "="*50)
            print("ТОП-10 ЧАСТЫХ:")
            print("-" * 50)

            for value, count in counter.most_common(10):
                percentage = (count / total) * 100
                print(f"  {value}: {count} раз ({percentage:.2f}%)")

            print("\n" + "="*60 + "\n")
        else:
            print("Dice не найдены в обновлениях")
            print("Возможно история очищена или лимит getUpdates")
    else:
        print(f"Ошибка API: {data}")
else:
    print(f"HTTP ошибка: {response.status_code}")

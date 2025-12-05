#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка РЕАЛЬНОГО каталога подарков через MTProto API
Это может показать подарки, недоступные через Bot API!
"""
import asyncio
import sys
from telethon import TelegramClient
from telethon.tl.functions.payments import GetStarGiftsRequest

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ВАЖНО: Нужны API credentials для пользователя (не бота!)
# Получить можно на https://my.telegram.org/apps
api_id = 0  # <<<< ЗАПОЛНИ ЭТО
api_hash = ''  # <<<< И ЭТО

async def check_star_gifts():
    print("=" * 70)
    print("ПРОВЕРКА РЕАЛЬНОГО КАТАЛОГА STAR GIFTS ЧЕРЕЗ MTPROTO API")
    print("=" * 70)

    if api_id == 0 or not api_hash:
        print("\n⚠️ ВНИМАНИЕ!")
        print("Для использования MTProto API нужны API credentials!")
        print("\nШаги:")
        print("1. Открой https://my.telegram.org/apps")
        print("2. Залогинься своим номером телефона")
        print("3. Создай приложение")
        print("4. Скопируй api_id и api_hash")
        print("5. Вставь их в этот скрипт (строки 16-17)")
        print("\nПосле этого запусти скрипт снова!")
        return

    client = TelegramClient('session_name', api_id, api_hash)

    try:
        await client.start()

        print("\n✅ Подключено к Telegram!")
        print("Запрашиваю каталог Star Gifts...")

        # Вызываем MTProto метод
        result = await client(GetStarGiftsRequest(hash=0))

        print(f"\n📦 Получено подарков: {len(result.gifts)}")

        # Группируем по количеству звезд
        star_counts = {}
        for gift in result.gifts:
            count = gift.stars
            if count not in star_counts:
                star_counts[count] = []
            star_counts[count].append(gift)

        print("\n" + "=" * 70)
        print("ДОСТУПНЫЕ ПОДАРКИ ПО КОЛИЧЕСТВУ ЗВЕЗД:")
        print("=" * 70)

        for stars in sorted(star_counts.keys()):
            gifts_list = star_counts[stars]
            print(f"\n⭐ {stars} Stars:")
            print(f"   Вариантов: {len(gifts_list)}")

            for i, gift in enumerate(gifts_list[:3], 1):
                print(f"\n   #{i}:")
                print(f"   - ID: {gift.id}")
                print(f"   - Stars: {gift.stars}")
                if hasattr(gift, 'availability_total') and gift.availability_total:
                    print(f"   - Всего выпущено: {gift.availability_total}")
                if hasattr(gift, 'availability_remains') and gift.availability_remains:
                    print(f"   - Осталось: {gift.availability_remains}")
                if hasattr(gift, 'sold_out') and gift.sold_out:
                    print(f"   - ❌ РАСПРОДАНО")

        print("\n" + "=" * 70)
        print(f"ИТОГО: найдено {len(star_counts)} различных номиналов")
        print(f"Номиналы: {sorted(star_counts.keys())}")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(check_star_gifts())

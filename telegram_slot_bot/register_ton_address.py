"""
Скрипт для регистрации TON адреса пользователя в базе данных
"""
import os
from dotenv import load_dotenv
from database import Database

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
db = Database(DATABASE_URL)

# Ваш Telegram ID (админ)
USER_ID = 7418707076

# Ваш TON адрес для получения выплат
TON_ADDRESS = "UQAVCfUrZ13mh1rLyhU_K45EHhYn-Ef_Ac4f4puP6zrB2xoP"

print("="*60)
print("РЕГИСТРАЦИЯ TON АДРЕСА")
print("="*60)
print()

# Проверяем существует ли пользователь
user = db.get_user(USER_ID)

if not user:
    print(f"[*] Создаем нового пользователя {USER_ID}...")
    db.create_user(USER_ID, "Admin", "Admin")
    print("[+] Пользователь создан!")
else:
    print(f"[+] Пользователь {USER_ID} найден!")

# Регистрируем TON адрес
print(f"[*] Регистрация TON адреса...")
db.set_user_ton_address(USER_ID, TON_ADDRESS, verified=True)

print()
print("="*60)
print("[+] ГОТОВО!")
print("="*60)
print()
print(f"User ID: {USER_ID}")
print(f"TON Address: {TON_ADDRESS}")
print()
print("[+] Теперь при выигрыше TON будут автоматически отправляться на этот адрес!")
print()

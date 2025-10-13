#!/usr/bin/env python3
"""
Утилита для генерации ключа шифрования для токенов HH.ru
"""
from cryptography.fernet import Fernet

if __name__ == "__main__":
    key = Fernet.generate_key()
    print("Сгенерирован новый ключ шифрования:")
    print(key.decode())
    print("\nДобавьте его в файл .env:")
    print(f"ENCRYPTION_KEY={key.decode()}")
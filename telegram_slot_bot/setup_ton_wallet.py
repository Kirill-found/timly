"""
Скрипт для настройки TON кошелька для бота
Позволяет создать новый кошелек или импортировать существующий
"""
import os
from tonsdk.contract.wallet import Wallets, WalletVersionEnum

def generate_new_wallet():
    """Генерация нового TON кошелька"""
    print("\n[*] Генерация нового TON кошелька...")
    print()

    # Генерируем новый кошелек
    mnemonics, pub_k, priv_k, wallet = Wallets.create(
        WalletVersionEnum.v4r2,
        workchain=0
    )

    address = wallet.address.to_string(True, True, True)

    print("="*60)
    print("НОВЫЙ TON КОШЕЛЕК СОЗДАН")
    print("="*60)
    print()
    print("[!] ВАЖНО: Сохраните эту информацию в безопасном месте!")
    print()
    print("Адрес кошелька:")
    print(f"  {address}")
    print()
    print("Seed-фраза (24 слова):")
    print(f"  {' '.join(mnemonics)}")
    print()
    print("="*60)
    print()
    print("[*] Добавьте эту seed-фразу в .env файл:")
    print()
    print(f'TON_WALLET_MNEMONIC="{' '.join(mnemonics)}"')
    print()
    print("[!] ВНИМАНИЕ:")
    print("  1. Пополните этот кошелек TON для оплаты комиссий")
    print("  2. Храните seed-фразу в безопасности!")
    print("  3. Не публикуйте .env файл в GitHub!")
    print()

def import_existing_wallet():
    """Импорт существующего TON кошелька"""
    print("\n[*] Импорт существующего TON кошелька...")
    print()
    print("Введите seed-фразу (24 слова, через пробел):")
    mnemonic_str = input("> ").strip()

    try:
        mnemonic_list = mnemonic_str.split()

        if len(mnemonic_list) != 24:
            print(f"\n[!] ОШИБКА: Должно быть 24 слова, получено {len(mnemonic_list)}")
            return

        # Импортируем кошелек
        mnemonics, pub_k, priv_k, wallet = Wallets.from_mnemonics(
            mnemonic_list,
            WalletVersionEnum.v4r2,
            workchain=0
        )

        address = wallet.address.to_string(True, True, True)

        print()
        print("="*60)
        print("КОШЕЛЕК ИМПОРТИРОВАН")
        print("="*60)
        print()
        print("Адрес кошелька:")
        print(f"  {address}")
        print()
        print("="*60)
        print()
        print("[*] Добавьте эту seed-фразу в .env файл:")
        print()
        print(f'TON_WALLET_MNEMONIC="{' '.join(mnemonic_list)}"')
        print()
        print("[!] ВНИМАНИЕ:")
        print("  1. Убедитесь что на кошельке достаточно TON для комиссий")
        print("  2. Не публикуйте .env файл в GitHub!")
        print()

    except Exception as e:
        print(f"\n[!] ОШИБКА при импорте: {e}")
        print("Проверьте правильность seed-фразы")

def main():
    print("="*60)
    print("НАСТРОЙКА TON КОШЕЛЬКА ДЛЯ СЛОТ-БОТА")
    print("="*60)
    print()
    print("Выберите действие:")
    print("  1. Создать новый TON кошелек")
    print("  2. Импортировать существующий кошелек")
    print("  3. Выход")
    print()

    choice = input("Ваш выбор (1-3): ").strip()

    if choice == "1":
        generate_new_wallet()
    elif choice == "2":
        import_existing_wallet()
    elif choice == "3":
        print("\nВыход...")
    else:
        print("\n[!] Неверный выбор")

    print()
    print("[*] Следующий шаг:")
    print("    1. Добавьте TON_WALLET_MNEMONIC в .env файл")
    print("    2. Добавьте TON_TESTNET=False (или True для тестовой сети)")
    print("    3. Пополните кошелек TON")
    print("    4. Перезапустите бота")
    print()

if __name__ == "__main__":
    main()

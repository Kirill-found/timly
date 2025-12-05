"""
Проверка какой адрес получается из seed-фразы
"""
from tonsdk.contract.wallet import Wallets, WalletVersionEnum

# Твоя seed-фраза
mnemonic = "base crouch cable jealous position travel protect dry country suit slight ignore panic river tornado shock oyster rebel evoke pilot alien orchard skirt gain".split()

print("="*60)
print("ПРОВЕРКА АДРЕСА ИЗ SEED-ФРАЗЫ")
print("="*60)
print()

# Пробуем разные версии кошелька
versions = [
    ("v3r1", WalletVersionEnum.v3r1),
    ("v3r2", WalletVersionEnum.v3r2),
    ("v4r1", WalletVersionEnum.v4r1),
    ("v4r2", WalletVersionEnum.v4r2),
]

for version_name, version_enum in versions:
    try:
        mnemonics, pub_k, priv_k, wallet = Wallets.from_mnemonics(
            mnemonic,
            version_enum,
            workchain=0
        )

        # Получаем адрес в разных форматах
        address_bounceable = wallet.address.to_string(True, True, True)
        address_non_bounceable = wallet.address.to_string(True, True, False)

        print(f"Версия: {version_name}")
        print(f"  Bounceable:     {address_bounceable}")
        print(f"  Non-bounceable: {address_non_bounceable}")
        print()

    except Exception as e:
        print(f"Ошибка для версии {version_name}: {e}")
        print()

print("="*60)
print("ОЖИДАЕМЫЙ АДРЕС:")
print("UQAVCfUrZ13mh1rLyhU_K45EHhYn-Ef_Ac4f4puP6zrB2xoP")
print("="*60)

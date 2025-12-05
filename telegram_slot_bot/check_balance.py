#!/usr/bin/env python3
"""
Простой скрипт для проверки баланса TON кошелька
"""
import asyncio
import os
from dotenv import load_dotenv
from ton_wallet import TONWallet

async def check_balance():
    load_dotenv()

    mnemonic = os.getenv('TON_WALLET_MNEMONIC')
    testnet = os.getenv('TON_TESTNET', 'False').lower() == 'true'

    wallet = TONWallet(mnemonic, testnet=testnet)
    await wallet.initialize()

    balance = await wallet.get_balance()

    print(f"\n{'='*50}")
    print(f"TON Wallet Address: {wallet.wallet.address.to_string(is_bounceable=False)}")
    print(f"Network: {'Testnet' if testnet else 'Mainnet'}")
    print(f"Balance: {balance} TON")
    print(f"{'='*50}\n")

    return balance

if __name__ == "__main__":
    asyncio.run(check_balance())

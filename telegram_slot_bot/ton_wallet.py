"""
Модуль для работы с TON блокчейном
Позволяет отправлять автоматические выплаты пользователям
"""
import os
import asyncio
import logging
from decimal import Decimal
from typing import Optional, Dict

from tonsdk.contract.wallet import Wallets, WalletVersionEnum
from tonsdk.utils import bytes_to_b64str, to_nano
from pytoniq import LiteBalancer, begin_cell
from pytoniq_core import Address

logger = logging.getLogger(__name__)

class TONWallet:
    """
    Класс для управления TON кошельком и отправки транзакций

    Использует hot wallet для автоматических выплат
    """

    def __init__(self, mnemonic: str, testnet: bool = False):
        """
        Инициализация кошелька

        Args:
            mnemonic: 24 слова seed-фразы кошелька
            testnet: Использовать тестовую сеть (по умолчанию False)
        """
        self.mnemonic = mnemonic.split()
        self.testnet = testnet
        self.provider = None
        self.wallet = None
        self.address = None

    async def initialize(self):
        """Инициализация подключения к сети TON"""
        try:
            # Создаем кошелек из мнемоники
            mnemonics, pub_k, priv_k, wallet = Wallets.from_mnemonics(
                self.mnemonic,
                WalletVersionEnum.v4r2,
                workchain=0
            )

            self.wallet = wallet
            self.address = wallet.address.to_string(True, True, True)

            # Подключаемся к LiteServer
            self.provider = LiteBalancer.from_mainnet_config(
                trust_level=2,
                timeout=15
            ) if not self.testnet else LiteBalancer.from_testnet_config(
                trust_level=2,
                timeout=15
            )

            await self.provider.start_up()

            logger.info(f"TON wallet initialized: {self.address}")
            logger.info(f"Network: {'Testnet' if self.testnet else 'Mainnet'}")

            # Проверяем баланс
            balance = await self.get_balance()
            logger.info(f"Current balance: {balance} TON")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize TON wallet: {e}")
            return False

    async def get_balance(self) -> Decimal:
        """
        Получить баланс кошелька

        Returns:
            Баланс в TON
        """
        try:
            if not self.provider or not self.wallet:
                raise Exception("Wallet not initialized")

            address_obj = Address(self.address)
            account_state = await self.provider.get_account_state(address_obj)

            # Конвертируем из nanoTON в TON
            balance_nano = account_state.balance
            balance_ton = Decimal(balance_nano) / Decimal(1_000_000_000)

            return balance_ton

        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return Decimal(0)

    async def send_ton(
        self,
        destination_address: str,
        amount_ton: float,
        comment: str = ""
    ) -> Optional[Dict]:
        """
        Отправить TON на указанный адрес

        Args:
            destination_address: Адрес получателя
            amount_ton: Сумма в TON
            comment: Комментарий к транзакции

        Returns:
            Словарь с информацией о транзакции или None при ошибке
        """
        try:
            if not self.provider or not self.wallet:
                raise Exception("Wallet not initialized")

            logger.info(f"Sending {amount_ton} TON to {destination_address}")

            # Проверяем баланс
            balance = await self.get_balance()
            if balance < Decimal(str(amount_ton)) + Decimal("0.01"):  # +0.01 TON на комиссию
                raise Exception(f"Insufficient balance: {balance} TON, need {amount_ton + 0.01} TON")

            # Получаем seqno кошелька
            address_obj = Address(self.address)
            account_state = await self.provider.get_account_state(address_obj)
            seqno = account_state.seqno if account_state.seqno else 0

            # Создаем тело транзакции с комментарием
            if comment:
                body = begin_cell().store_uint(0, 32).store_string(comment).end_cell()
            else:
                body = begin_cell().end_cell()

            # Создаем транзакцию
            query = self.wallet.create_transfer_message(
                destination_address,
                to_nano(amount_ton, "ton"),
                seqno,
                payload=body
            )

            # Отправляем транзакцию
            await self.provider.send_message(query["message"].to_boc(False))

            logger.info(f"Transaction sent! Seqno: {seqno}")

            # Ждем подтверждения (максимум 60 секунд)
            confirmed = await self._wait_for_transaction(seqno)

            if confirmed:
                result = {
                    "success": True,
                    "seqno": seqno,
                    "destination": destination_address,
                    "amount": amount_ton,
                    "comment": comment,
                    "hash": None  # В pytoniq нет прямого способа получить hash до подтверждения
                }
                logger.info(f"Transaction confirmed: {result}")
                return result
            else:
                raise Exception("Transaction confirmation timeout")

        except Exception as e:
            logger.error(f"Failed to send TON: {e}")
            return None

    async def _wait_for_transaction(self, expected_seqno: int, timeout: int = 60) -> bool:
        """
        Ожидание подтверждения транзакции

        Args:
            expected_seqno: Ожидаемый seqno после транзакции
            timeout: Максимальное время ожидания в секундах

        Returns:
            True если транзакция подтверждена
        """
        try:
            address_obj = Address(self.address)
            start_time = asyncio.get_event_loop().time()

            while True:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    logger.warning("Transaction confirmation timeout")
                    return False

                account_state = await self.provider.get_account_state(address_obj)
                current_seqno = account_state.seqno if account_state.seqno else 0

                if current_seqno > expected_seqno:
                    logger.info(f"Transaction confirmed! New seqno: {current_seqno}")
                    return True

                await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"Error waiting for transaction: {e}")
            return False

    async def close(self):
        """Закрыть соединение с провайдером"""
        if self.provider:
            await self.provider.close_all()
            logger.info("TON provider connection closed")


class TONPaymentService:
    """
    Сервис для управления автоматическими выплатами

    Конвертирует внутриигровые Stars в TON и отправляет пользователям
    """

    # Курс конвертации: 1 Star = X TON
    # Можно настроить под ваши нужды
    STARS_TO_TON_RATE = 0.001  # 1 Star = 0.001 TON (1000 Stars = 1 TON)

    def __init__(self, wallet: TONWallet):
        """
        Args:
            wallet: Инициализированный TON кошелек
        """
        self.wallet = wallet

    def stars_to_ton(self, stars: int) -> float:
        """
        Конвертировать Stars в TON

        Args:
            stars: Количество Stars

        Returns:
            Эквивалент в TON
        """
        return stars * self.STARS_TO_TON_RATE

    async def send_payout(
        self,
        user_ton_address: str,
        stars_amount: int,
        user_id: int
    ) -> Optional[Dict]:
        """
        Отправить выплату пользователю

        Args:
            user_ton_address: TON адрес пользователя
            stars_amount: Количество Stars для конвертации
            user_id: Telegram ID пользователя (для комментария)

        Returns:
            Информация о транзакции или None при ошибке
        """
        try:
            ton_amount = self.stars_to_ton(stars_amount)

            # Минимальная сумма для отправки - 0.01 TON
            if ton_amount < 0.01:
                logger.warning(f"Amount too small: {ton_amount} TON (min 0.01 TON)")
                return None

            comment = f"Slot game win: {stars_amount} stars | User: {user_id}"

            result = await self.wallet.send_ton(
                destination_address=user_ton_address,
                amount_ton=ton_amount,
                comment=comment
            )

            return result

        except Exception as e:
            logger.error(f"Failed to send payout: {e}")
            return None

    async def check_balance_sufficient(self, stars_amount: int) -> bool:
        """
        Проверить достаточно ли баланса для выплаты

        Args:
            stars_amount: Количество Stars для конвертации

        Returns:
            True если баланса достаточно
        """
        try:
            ton_amount = self.stars_to_ton(stars_amount)
            balance = await self.wallet.get_balance()

            # +0.01 TON на комиссию
            return balance >= Decimal(str(ton_amount)) + Decimal("0.01")

        except Exception as e:
            logger.error(f"Failed to check balance: {e}")
            return False

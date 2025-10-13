"""
Сервис шифрования для HH.ru токенов
КРИТИЧНО: все токены должны храниться в зашифрованном виде
"""
from cryptography.fernet import Fernet
import os
import base64
import logging
from dotenv import load_dotenv

# Загружаем .env файл перед использованием os.getenv
load_dotenv()

logger = logging.getLogger(__name__)


class TokenEncryption:
    """
    Шифрование HH.ru API токенов
    Использует Fernet (симметричное шифрование)
    """

    def __init__(self):
        self.cipher = self._get_cipher()

    def _get_cipher(self) -> Fernet:
        """Получение cipher с ключом из окружения"""
        key = os.getenv("ENCRYPTION_KEY")

        if not key:
            # Генерация ключа для разработки (НЕ для production!)
            if os.getenv("APP_ENV") == "development":
                logger.warning("Генерируется новый ключ шифрования для разработки")
                key = Fernet.generate_key().decode()
                logger.warning(f"ENCRYPTION_KEY={key}")
            else:
                raise ValueError("ENCRYPTION_KEY обязателен в production")

        try:
            # Проверяем, что ключ в правильном формате
            if isinstance(key, str):
                key = key.encode()
            return Fernet(key)
        except Exception as e:
            logger.error(f"Ошибка создания cipher: {e}")
            raise ValueError("Неверный формат ENCRYPTION_KEY")

    def encrypt(self, token: str) -> str:
        """
        Шифрование HH.ru API токена

        Args:
            token: Открытый токен

        Returns:
            str: Зашифрованный токен (base64)
        """
        if not token or not isinstance(token, str):
            raise ValueError("Токен должен быть непустой строкой")

        try:
            encrypted = self.cipher.encrypt(token.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Ошибка шифрования токена: {e}")
            raise ValueError("Не удалось зашифровать токен")

    def decrypt(self, encrypted_token: str) -> str:
        """
        Расшифровка HH.ru API токена

        Args:
            encrypted_token: Зашифрованный токен

        Returns:
            str: Открытый токен
        """
        if not encrypted_token or not isinstance(encrypted_token, str):
            raise ValueError("Зашифрованный токен должен быть непустой строкой")

        try:
            decrypted = self.cipher.decrypt(encrypted_token.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Ошибка расшифровки токена: {e}")
            raise ValueError("Не удалось расшифровать токен")

    def is_valid_encrypted_token(self, encrypted_token: str) -> bool:
        """
        Проверка валидности зашифрованного токена
        Пытается расшифровать без выброса исключения

        Args:
            encrypted_token: Зашифрованный токен для проверки

        Returns:
            bool: True если токен можно расшифровать
        """
        try:
            self.decrypt(encrypted_token)
            return True
        except Exception:
            return False


# Singleton instance для использования в других модулях
token_encryption = TokenEncryption()
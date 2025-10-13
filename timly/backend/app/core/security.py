"""
Модуль безопасности: JWT, хеширование паролей, шифрование токенов
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.core.config import settings

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Шифровальщик для HH.ru токенов
fernet = Fernet(settings.encryption_key.encode() if len(settings.encryption_key) == 44 
                else Fernet.generate_key())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Создание JWT токена
    
    Args:
        data: Данные для кодирования в токен
        expires_delta: Время жизни токена
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Проверка и декодирование JWT токена
    
    Returns:
        Декодированные данные токена или None если токен невалидный
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def encrypt_hh_token(token: str) -> str:
    """
    Шифрование HH.ru токена для безопасного хранения
    
    Args:
        token: Открытый токен HH.ru
        
    Returns:
        Зашифрованный токен
    """
    return fernet.encrypt(token.encode()).decode()


def decrypt_hh_token(encrypted_token: str) -> str:
    """
    Расшифровка HH.ru токена
    
    Args:
        encrypted_token: Зашифрованный токен
        
    Returns:
        Расшифрованный токен
    """
    return fernet.decrypt(encrypted_token.encode()).decode()
"""
Сервис аутентификации и управления пользователями
JWT токены, регистрация, работа с HH.ru токенами
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import asyncio
from functools import partial
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.models.user import User
from app.schemas.auth import UserRegistration
from app.services.encryption import token_encryption
from app.services.hh_client import HHClient
from app.utils.exceptions import AuthenticationError, ValidationError

logger = logging.getLogger(__name__)

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Сервис аутентификации пользователей
    Управление JWT токенами, паролями и HH.ru интеграцией
    """

    def __init__(self, db: Session):
        self.db = db

    # Работа с паролями (async wrappers для blocking operations)
    async def _hash_password(self, password: str) -> str:
        """Хеширование пароля (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            partial(pwd_context.hash, password)
        )

    async def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля (async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            partial(pwd_context.verify, plain_password, hashed_password)
        )

    # JWT токены
    def _create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Создание JWT access токена"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    def _create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Создание JWT refresh токена"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })

        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    def _decode_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Декодирование JWT токена с проверкой истечения

        Args:
            token: JWT токен
            token_type: Тип токена (access или refresh)

        Raises:
            AuthenticationError: При невалидном или истекшем токене
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # Проверка типа токена
            if payload.get("type") != token_type:
                raise AuthenticationError(f"Неверный тип токена. Ожидается {token_type}")

            # Проверка exp уже делается автоматически в jwt.decode
            # но для ясности можно добавить явную проверку
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                raise AuthenticationError("Токен истек")

            return payload

        except ExpiredSignatureError:
            raise AuthenticationError("Токен истек")
        except JWTError as e:
            logger.warning(f"JWT decode error: {e}")
            raise AuthenticationError("Недействительный токен")

    # Регистрация и аутентификация
    async def register_user(self, user_data: UserRegistration) -> User:
        """
        Регистрация нового пользователя

        Args:
            user_data: Данные для регистрации

        Returns:
            User: Созданный пользователь

        Raises:
            ValidationError: Если пользователь уже существует
        """
        try:
            # Проверка существования пользователя
            existing_user = self.db.query(User).filter(
                User.email == user_data.email
            ).first()

            if existing_user:
                raise ValidationError("Пользователь с таким email уже существует")

            # Создание нового пользователя с async хешированием
            hashed_password = await self._hash_password(user_data.password)

            new_user = User(
                email=user_data.email,
                password_hash=hashed_password,
                company_name=user_data.company_name
            )

            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            logger.info(f"Зарегистрирован новый пользователь: {new_user.email}")

            # Автоматическое создание Trial подписки
            try:
                from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus, PlanType
                from datetime import timedelta
                import uuid as uuid_lib

                # Получаем Trial план
                trial_plan = self.db.query(SubscriptionPlan).filter(
                    SubscriptionPlan.plan_type == PlanType.trial
                ).first()

                if trial_plan:
                    # Создаём Trial подписку на 30 дней с лимитом 50 анализов
                    trial_subscription = Subscription(
                        id=uuid_lib.uuid4(),
                        user_id=new_user.id,
                        plan_id=trial_plan.id,
                        status=SubscriptionStatus.trial,
                        started_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=30),
                        analyses_used_this_month=0,
                        exports_used_this_month=0
                    )
                    self.db.add(trial_subscription)
                    self.db.commit()
                    logger.info(f"Trial подписка создана для пользователя: {new_user.email}")
                else:
                    logger.warning("Trial план не найден в базе данных")

            except Exception as e:
                logger.error(f"Не удалось создать Trial подписку: {e}")
                # Не прерываем регистрацию, если не удалось создать подписку

            # Отправляем уведомление в Telegram
            try:
                from app.services.telegram_service import notify_new_user
                await notify_new_user(new_user.email, new_user.company_name)
            except Exception as e:
                logger.error(f"Не удалось отправить Telegram уведомление: {e}")

            return new_user

        except IntegrityError:
            self.db.rollback()
            raise ValidationError("Пользователь с таким email уже существует")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка регистрации пользователя: {e}")
            raise

    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Аутентификация пользователя

        Args:
            email: Email пользователя
            password: Пароль

        Returns:
            Dict: Access token, refresh token и метаданные

        Raises:
            AuthenticationError: Если аутентификация не удалась
        """
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            raise AuthenticationError("Неверный email или пароль")

        # Async проверка пароля
        if not await self._verify_password(password, user.password_hash):
            raise AuthenticationError("Неверный email или пароль")

        if not user.is_active:
            raise AuthenticationError("Аккаунт заблокирован")

        # Обновление времени последнего входа
        user.last_login_at = datetime.utcnow()
        self.db.commit()

        # Создание JWT токенов
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        }

        access_token = self._create_access_token(token_data)
        refresh_token = self._create_refresh_token({"sub": str(user.id)})

        logger.info(f"Пользователь аутентифицирован: {user.email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Обновление access токена используя refresh токен

        Args:
            refresh_token: Refresh токен

        Returns:
            Dict: Новый access token и метаданные

        Raises:
            AuthenticationError: При невалидном refresh токене
        """
        try:
            # Декодирование refresh токена
            payload = self._decode_token(refresh_token, token_type="refresh")
            user_id = payload.get("sub")

            if not user_id:
                raise AuthenticationError("Неверный refresh токен")

            # Получение пользователя
            user = self.db.query(User).filter(User.id == user_id).first()

            if not user or not user.is_active:
                raise AuthenticationError("Пользователь не найден или заблокирован")

            # Создание нового access токена
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value
            }

            access_token = self._create_access_token(token_data)

            logger.info(f"Access токен обновлен для пользователя: {user.email}")

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }

        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Ошибка обновления токена: {e}")
            raise AuthenticationError("Не удалось обновить токен")

    async def get_current_user(self, token: str) -> Optional[User]:
        """
        Получение текущего пользователя по JWT токену с проверкой истечения

        Args:
            token: JWT токен

        Returns:
            User: Пользователь или None
        """
        try:
            import uuid as uuid_lib
            payload = self._decode_token(token, token_type="access")
            user_id_str = payload.get("sub")

            if not user_id_str:
                return None

            # Конвертируем строку в UUID объект
            user_id = uuid_lib.UUID(user_id_str)
            user = self.db.query(User).filter(User.id == user_id).first()

            if not user or not user.is_active:
                return None

            return user

        except AuthenticationError as e:
            logger.debug(f"Ошибка аутентификации: {e}")
            return None

    # Работа с HH.ru токенами
    async def update_hh_token(self, user_id: str, hh_token: str) -> Dict[str, Any]:
        """
        Обновление HH.ru токена пользователя

        Args:
            user_id: ID пользователя
            hh_token: Новый HH.ru токен

        Returns:
            Dict: Результат операции
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValidationError("Пользователь не найден")

            # Тестирование токена перед сохранением
            hh_client = HHClient(hh_token)
            validation_result = await hh_client.test_connection()

            if not validation_result["is_valid"]:
                raise ValidationError(f"Недействительный HH.ru токен: {validation_result['error_message']}")

            # Шифрование и сохранение токена
            encrypted_token = token_encryption.encrypt(hh_token)

            user.encrypted_hh_token = encrypted_token
            user.token_verified = True
            user.token_verified_at = datetime.utcnow()

            self.db.commit()

            logger.info(f"HH.ru токен обновлен для пользователя: {user.email}")

            return {
                "status": "success",
                "message": "HH.ru токен успешно сохранен и проверен",
                "employer_name": validation_result.get("employer_name")
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка обновления HH.ru токена: {e}")
            raise

    async def delete_hh_token(self, user_id: str) -> Dict[str, Any]:
        """
        Удаление HH.ru токена

        Args:
            user_id: ID пользователя

        Returns:
            Dict: Результат операции
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValidationError("Пользователь не найден")

            user.encrypted_hh_token = None
            user.token_verified = False
            user.token_verified_at = None

            self.db.commit()

            logger.info(f"HH.ru токен удален для пользователя: {user.email}")

            return {
                "status": "success",
                "message": "HH.ru токен успешно удален"
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка удаления HH.ru токена: {e}")
            raise

    async def get_hh_client(self, user_id: str) -> HHClient:
        """
        Получение HH клиента для пользователя

        Args:
            user_id: ID пользователя

        Returns:
            HHClient: Готовый к использованию клиент

        Raises:
            ValidationError: Если токен не настроен
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.has_hh_token:
            raise ValidationError("HH.ru токен не настроен")

        decrypted_token = token_encryption.decrypt(user.encrypted_hh_token)
        return HHClient(decrypted_token)

    # Дополнительные методы
    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> Dict[str, Any]:
        """
        Смена пароля пользователя

        Args:
            user_id: ID пользователя
            current_password: Текущий пароль
            new_password: Новый пароль

        Returns:
            Dict: Результат операции
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValidationError("Пользователь не найден")

            # Async проверка текущего пароля
            if not await self._verify_password(current_password, user.password_hash):
                raise AuthenticationError("Неверный текущий пароль")

            # Async хеширование нового пароля
            user.password_hash = await self._hash_password(new_password)
            self.db.commit()

            logger.info(f"Пароль изменен для пользователя: {user.email}")

            return {
                "status": "success",
                "message": "Пароль успешно изменен"
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка смены пароля: {e}")
            raise

    async def revoke_tokens(self, user_id: str) -> Dict[str, Any]:
        """
        Отзыв всех токенов пользователя (logout)

        Note: В текущей реализации JWT stateless, поэтому
        для полноценного revoke нужен blacklist в Redis.
        Это TODO для будущей реализации.

        Args:
            user_id: ID пользователя

        Returns:
            Dict: Результат операции
        """
        # TODO: Реализовать blacklist токенов в Redis
        logger.info(f"Отзыв токенов для пользователя: {user_id}")

        return {
            "status": "success",
            "message": "Токены отозваны (клиентская сторона должна удалить токены)"
        }
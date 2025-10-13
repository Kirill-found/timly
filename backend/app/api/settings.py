"""
API endpoints для настроек пользователя
Управление настройками аккаунта и интеграций
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import update
from typing import Dict, Any
from datetime import datetime
import logging

from app.database import get_db
from app.api.auth import get_current_user
from app.schemas.base import APIResponse
from app.services.auth_service import AuthService
from app.services.encryption import token_encryption
from app.services.hh_client import HHClient
from app.models.user import User
from app.schemas.hh import (
    HHTokenCreate,
    HHTokenResponse,
    HHIntegrationStatus,
    HHTokenValidation
)
from app.utils.exceptions import HHIntegrationError
from app.utils.response import success, created, bad_request, unauthorized, not_found, internal_error

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=APIResponse)
async def get_settings(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение всех настроек пользователя
    Включает настройки профиля, интеграций и уведомлений
    """
    # TODO: Реализовать получение настроек пользователя
    return success(data={
        "status": "TODO",
        "message": "Получение настроек будет реализовано",
        "user_id": str(current_user.id),
        "settings": {
            "notifications": {
                "email_enabled": True,
                "new_applications": True,
                "analysis_complete": True
            },
            "analysis": {
                "auto_analyze": True,
                "min_score_threshold": 70,
                "preferred_language": "ru"
            },
            "export": {
                "default_format": "xlsx",
                "include_resume_data": False
            }
        }
    })


@router.put("/", response_model=APIResponse)
async def update_settings(
    settings_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновление настроек пользователя
    Принимает частичное обновление настроек
    """
    # TODO: Реализовать обновление настроек
    return success(data={
        "status": "TODO",
        "message": "Обновление настроек будет реализовано",
        "updated_settings": settings_data
    })


@router.get("/notifications", response_model=APIResponse)
async def get_notification_settings(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение настроек уведомлений
    Email и push уведомления
    """
    # TODO: Реализовать настройки уведомлений
    return success(data={
        "status": "TODO",
        "message": "Настройки уведомлений будут реализованы",
        "notifications": {
            "email_enabled": True,
            "email": current_user.email,
            "new_applications": True,
            "analysis_complete": True,
            "weekly_summary": False
        }
    })


@router.put("/notifications", response_model=APIResponse)
async def update_notification_settings(
    notification_data: Dict[str, Any],
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновление настроек уведомлений
    Включение/выключение различных типов уведомлений
    """
    # TODO: Реализовать обновление настроек уведомлений
    return success(data={
        "status": "TODO",
        "message": "Обновление настроек уведомлений будет реализовано",
        "updated_notifications": notification_data
    })


@router.get("/integrations", response_model=APIResponse)
async def get_integration_settings(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение статуса интеграций
    HH.ru, Telegram, Slack и другие интеграции
    """
    return success(data={
        "integrations": {
            "hh_ru": {
                "connected": current_user.has_hh_token,
                "verified": current_user.token_verified,
                "last_sync": None  # TODO: Добавить дату последней синхронизации
            },
            "telegram": {
                "connected": False,
                "bot_username": "@timly_notifications_bot"
            },
            "slack": {
                "connected": False,
                "webhook_url": None
            }
        }
    })


@router.get("/hh-token/status", response_model=APIResponse)
async def get_hh_token_status(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Проверка статуса HH.ru токена
    Проверяет валидность без повторного сохранения
    """
    try:
        auth_service = AuthService(db)
        status_info = await auth_service.check_hh_token_status(current_user.id)
        return success(data=status_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Ошибка при проверке статуса HH.ru токена"
            }
        )


@router.post("/reset", response_model=APIResponse)
async def reset_settings(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Сброс настроек к значениям по умолчанию
    Не затрагивает HH.ru токен и профильные данные
    """
    # TODO: Реализовать сброс настроек
    return success(data={
        "status": "TODO",
        "message": "Сброс настроек будет реализован",
        "reset_sections": [
            "notifications",
            "analysis_preferences",
            "export_settings"
        ]
    })


# ==================== HH.ru TOKEN MANAGEMENT ENDPOINTS ====================

async def _validate_hh_token(token: str) -> HHTokenValidation:
    """
    Внутренняя функция для валидации HH.ru токена
    Проверяет токен через запрос к API HH.ru
    """
    try:
        async with HHClient(token) as hh_client:
            # Тестовый запрос к API для проверки токена
            user_info = await hh_client.get_employer_info()

            if user_info and 'name' in user_info:
                return HHTokenValidation(
                    is_valid=True,
                    employer_name=user_info.get('name'),
                    error_message=None
                )
            else:
                return HHTokenValidation(
                    is_valid=False,
                    employer_name=None,
                    error_message="Не удалось получить информацию о компании"
                )

    except HHIntegrationError as e:
        logger.warning(f"HH.ru token validation failed: {e}")
        return HHTokenValidation(
            is_valid=False,
            employer_name=None,
            error_message=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during HH.ru token validation: {e}")
        return HHTokenValidation(
            is_valid=False,
            employer_name=None,
            error_message="Ошибка при проверке токена"
        )


@router.post("/hh-token", response_model=APIResponse)
async def save_hh_token(
    token_data: HHTokenCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Сохранение зашифрованного HH.ru токена
    КРИТИЧНО: токен шифруется перед сохранением в БД
    """
    try:
        # Валидация токена через HH.ru API
        validation_result = await _validate_hh_token(token_data.token)

        if not validation_result.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INVALID_HH_TOKEN",
                    "message": validation_result.error_message or "Токен недействителен"
                }
            )

        # Шифрование токена
        try:
            encrypted_token = token_encryption.encrypt(token_data.token)
        except Exception as e:
            logger.error(f"Token encryption failed for user {current_user.id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "ENCRYPTION_ERROR",
                    "message": "Ошибка при шифровании токена"
                }
            )

        # Сохранение в БД
        try:
            db.execute(
                update(User)
                .where(User.id == current_user.id)
                .values(
                    encrypted_hh_token=encrypted_token,
                    token_verified=True,
                    token_verified_at=datetime.utcnow(),
                    company_name=validation_result.employer_name,
                    updated_at=datetime.utcnow()
                )
            )
            db.commit()

            logger.info(f"HH.ru token saved and verified for user {current_user.id}")

        except Exception as e:
            logger.error(f"Database error saving HH token for user {current_user.id}: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "DATABASE_ERROR",
                    "message": "Ошибка при сохранении токена"
                }
            )

        return success(data={
            "success": True,
            "token_verified": True,
            "employer_name": validation_result.employer_name,
            "message": "Токен успешно сохранен и верифицирован"
        })

    except HTTPException:
        # Пробрасываем HTTP исключения как есть
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving HH token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Внутренняя ошибка сервера"
            }
        )


@router.get("/status", response_model=APIResponse)
async def get_integration_status(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение статуса интеграции с HH.ru
    Показывает информацию о токене без его раскрытия
    """
    try:
        # Получаем свежие данные пользователя из БД
        user = db.query(User).filter(User.id == current_user.id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "USER_NOT_FOUND",
                    "message": "Пользователь не найден"
                }
            )

        return success(data={
            "has_token": user.encrypted_hh_token is not None,
            "token_verified": user.token_verified,
            "employer_name": user.company_name,
            "token_verified_at": user.token_verified_at.isoformat() if user.token_verified_at else None,
            "last_sync_at": None  # TODO: добавить отслеживание последней синхронизации
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting integration status for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Ошибка при получении статуса интеграции"
            }
        )


@router.delete("/hh-token", response_model=APIResponse)
async def delete_hh_token(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удаление HH.ru токена из системы
    Полностью стирает зашифрованный токен
    """
    try:
        # Удаление токена из БД
        db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(
                encrypted_hh_token=None,
                token_verified=False,
                token_verified_at=None,
                updated_at=datetime.utcnow()
            )
        )
        db.commit()

        logger.info(f"HH.ru token deleted for user {current_user.id}")

        return success(data={
            "success": True,
            "message": "Токен HH.ru успешно удален"
        })

    except Exception as e:
        logger.error(f"Error deleting HH token for user {current_user.id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DATABASE_ERROR",
                "message": "Ошибка при удалении токена"
            }
        )


@router.post("/hh-token/validate", response_model=APIResponse)
async def validate_current_token(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Проверка валидности текущего сохраненного HH.ru токена
    Делает тестовый запрос к HH.ru API
    """
    try:
        # Получаем пользователя с токеном
        user = db.query(User).filter(User.id == current_user.id).first()

        if not user or not user.encrypted_hh_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "TOKEN_NOT_FOUND",
                    "message": "HH.ru токен не найден"
                }
            )

        # Расшифровываем токен
        try:
            decrypted_token = token_encryption.decrypt(user.encrypted_hh_token)
        except Exception as e:
            logger.error(f"Token decryption failed for user {current_user.id}: {e}")
            # Помечаем токен как невалидный
            db.execute(
                update(User)
                .where(User.id == current_user.id)
                .values(token_verified=False, updated_at=datetime.utcnow())
            )
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "DECRYPTION_ERROR",
                    "message": "Не удалось расшифровать сохраненный токен"
                }
            )

        # Валидируем токен через HH.ru API
        validation_result = await _validate_hh_token(decrypted_token)

        # Обновляем статус верификации в БД
        db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(
                token_verified=validation_result.is_valid,
                token_verified_at=datetime.utcnow() if validation_result.is_valid else None,
                company_name=validation_result.employer_name if validation_result.is_valid else user.company_name,
                updated_at=datetime.utcnow()
            )
        )
        db.commit()

        return success(data={
            "is_valid": validation_result.is_valid,
            "employer_name": validation_result.employer_name,
            "error_message": validation_result.error_message
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating HH token for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "Ошибка при проверке токена"
            }
        )
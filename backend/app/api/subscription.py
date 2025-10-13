"""
API endpoints для управления подписками и тарификацией
Получение планов, текущей подписки, обновление тарифа, статистика использования
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.subscription import PlanType, SubscriptionStatus
from app.services.subscription_service import SubscriptionService
from app.schemas.base import APIResponse
from app.utils.response import success, bad_request, not_found
from app.utils.exceptions import ValidationError

router = APIRouter()


# Pydantic schemas для запросов
class UpgradeSubscriptionRequest(BaseModel):
    """Запрос на смену тарифного плана"""
    plan_type: str  # free, starter, professional, enterprise
    duration_months: int = 1  # 1 или 12

    class Config:
        json_schema_extra = {
            "example": {
                "plan_type": "professional",
                "duration_months": 12
            }
        }


@router.get("/plans", response_model=APIResponse)
async def get_subscription_plans(
    db: Session = Depends(get_db)
):
    """
    Получить список всех доступных тарифных планов

    Возвращает информацию о тарифах, ценах и лимитах
    """
    try:
        service = SubscriptionService(db)
        plans = await service.get_all_plans()

        return success(data={
            "plans": [plan.to_dict() for plan in plans]
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "PLANS_FETCH_ERROR",
                "message": "Ошибка при получении тарифных планов"
            }
        )


@router.get("/current", response_model=APIResponse)
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить текущую подписку пользователя

    Возвращает:
    - Информацию о текущем тарифе
    - Использование лимитов
    - Дату окончания подписки
    """
    try:
        service = SubscriptionService(db)
        subscription = await service.get_or_create_subscription(current_user.id)

        return success(data={
            "subscription": subscription.to_dict()
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "SUBSCRIPTION_FETCH_ERROR",
                "message": "Ошибка при получении подписки"
            }
        )


@router.post("/upgrade", response_model=APIResponse)
async def upgrade_subscription(
    request: UpgradeSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновление тарифного плана

    Позволяет пользователю перейти на другой тариф.
    В реальной системе здесь должна быть интеграция с платёжной системой.

    Args:
        plan_type: Тип нового плана (free, starter, professional, enterprise)
        duration_months: Длительность подписки (1 или 12 месяцев)
    """
    try:
        # Валидация типа плана
        try:
            plan_type_enum = PlanType[request.plan_type]
        except KeyError:
            return bad_request(
                error="INVALID_PLAN_TYPE",
                message=f"Неверный тип тарифа: {request.plan_type}"
            )

        # Валидация длительности
        if request.duration_months not in [1, 12]:
            return bad_request(
                error="INVALID_DURATION",
                message="Длительность подписки может быть 1 или 12 месяцев"
            )

        service = SubscriptionService(db)

        # Обновляем подписку
        new_subscription = await service.upgrade_subscription(
            user_id=current_user.id,
            new_plan_type=plan_type_enum,
            duration_months=request.duration_months
        )

        return success(data={
            "subscription": new_subscription.to_dict(),
            "message": f"Подписка успешно обновлена на тариф {new_subscription.plan.name}"
        })

    except ValidationError as e:
        return bad_request(error="VALIDATION_ERROR", message=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "UPGRADE_ERROR",
                "message": "Ошибка при обновлении подписки"
            }
        )


@router.get("/usage", response_model=APIResponse)
async def get_usage_statistics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить статистику использования

    Args:
        days: Количество дней для анализа (по умолчанию 30)

    Возвращает:
    - Общее количество использований по типам
    - Детализацию по дням
    - Информацию о подписке и лимитах
    """
    try:
        # Валидация параметра days
        if days < 1 or days > 365:
            return bad_request(
                error="INVALID_DAYS",
                message="Параметр days должен быть от 1 до 365"
            )

        service = SubscriptionService(db)
        statistics = await service.get_usage_statistics(
            user_id=current_user.id,
            days=days
        )

        return success(data=statistics)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "STATISTICS_ERROR",
                "message": "Ошибка при получении статистики"
            }
        )


@router.get("/limits/check", response_model=APIResponse)
async def check_limits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Проверить все лимиты текущего пользователя

    Возвращает статус доступности различных операций:
    - Возможность анализа
    - Возможность экспорта
    - Возможность создания вакансий
    """
    try:
        service = SubscriptionService(db)

        can_analyze, analyze_msg = await service.check_can_analyze(current_user.id)
        can_export, export_msg = await service.check_can_export(current_user.id)
        can_add_vacancy, vacancy_msg = await service.check_vacancy_limit(current_user.id)

        return success(data={
            "can_analyze": can_analyze,
            "can_export": can_export,
            "can_add_vacancy": can_add_vacancy,
            "messages": {
                "analyze": analyze_msg,
                "export": export_msg,
                "vacancy": vacancy_msg
            }
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "LIMITS_CHECK_ERROR",
                "message": "Ошибка при проверке лимитов"
            }
        )


@router.post("/cancel", response_model=APIResponse)
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Отменить текущую подписку

    Подписка будет отменена, но останется активной до конца оплаченного периода.
    После окончания периода автоматически будет создана бесплатная подписка.
    """
    try:
        service = SubscriptionService(db)
        subscription = await service.get_or_create_subscription(current_user.id)

        # Нельзя отменить уже отменённую или истёкшую подписку
        if subscription.status in [SubscriptionStatus.cancelled, SubscriptionStatus.expired]:
            return bad_request(
                error="ALREADY_CANCELLED",
                message="Подписка уже отменена или истекла"
            )

        # Нельзя отменить бесплатную подписку
        if subscription.plan.plan_type == PlanType.free:
            return bad_request(
                error="CANNOT_CANCEL_FREE",
                message="Невозможно отменить бесплатную подписку"
            )

        # Отменяем подписку
        from datetime import datetime
        subscription.status = SubscriptionStatus.cancelled
        subscription.cancelled_at = datetime.utcnow()
        db.commit()

        return success(data={
            "subscription": subscription.to_dict(),
            "message": f"Подписка отменена. Доступ сохранится до {subscription.expires_at.strftime('%d.%m.%Y')}"
        })

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CANCEL_ERROR",
                "message": "Ошибка при отмене подписки"
            }
        )

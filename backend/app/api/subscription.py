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
    plan_type: Optional[str] = None  # free, starter, professional, enterprise
    new_plan_type: Optional[str] = None  # Для обратной совместимости
    duration_months: int = 1  # 1 или 12

    def get_plan_type(self) -> str:
        """Получить тип плана из любого доступного поля"""
        return self.plan_type or self.new_plan_type or ""

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
        # Получаем тип плана из любого доступного поля
        plan_type_str = request.get_plan_type()
        if not plan_type_str:
            return bad_request(
                error="MISSING_PLAN_TYPE",
                message="Необходимо указать plan_type или new_plan_type"
            )

        # Валидация типа плана
        try:
            plan_type_enum = PlanType[plan_type_str]
        except KeyError:
            return bad_request(
                error="INVALID_PLAN_TYPE",
                message=f"Неверный тип тарифа: {plan_type_str}"
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

        # Получаем текущую подписку
        subscription = await service.get_or_create_subscription(current_user.id)

        # Считаем анализы из таблицы analysis_results за текущий период подписки
        from app.models.application import AnalysisResult, Application
        from app.models.vacancy import Vacancy
        from datetime import datetime, timedelta
        from sqlalchemy import func

        # Определяем начало текущего периода
        if subscription and subscription.started_at:
            period_start = subscription.started_at
        else:
            # Если нет started_at, берём начало текущего месяца
            now = datetime.utcnow()
            period_start = datetime(now.year, now.month, 1)

        # Считаем количество анализов за период (через JOIN с applications и vacancies)
        analyses_used = db.query(func.count(AnalysisResult.id))\
            .join(Application, AnalysisResult.application_id == Application.id)\
            .join(Vacancy, Application.vacancy_id == Vacancy.id)\
            .filter(
                Vacancy.user_id == current_user.id,
                AnalysisResult.created_at >= period_start
            ).scalar() or 0

        # Вычисляем оставшиеся анализы
        if subscription and subscription.plan:
            max_analyses = subscription.plan.max_analyses_per_month
            is_unlimited = max_analyses == -1

            if is_unlimited:
                analyses_remaining = -1
                analyses_limit = -1
            else:
                analyses_limit = max_analyses
                analyses_remaining = max(0, max_analyses - analyses_used)

            # Дата обновления лимита
            from dateutil.relativedelta import relativedelta

            if subscription.expires_at:
                reset_date = (subscription.expires_at + timedelta(days=1)).isoformat()
            else:
                reset_date = (datetime.utcnow() + relativedelta(months=1)).isoformat()
        else:
            # Нет подписки - бесплатный план
            analyses_limit = 10  # Лимит free плана
            analyses_remaining = max(0, analyses_limit - analyses_used)
            is_unlimited = False
            reset_date = None

        return success(data={
            "can_analyze": can_analyze,
            "can_export": can_export,
            "can_add_vacancy": can_add_vacancy,
            "messages": {
                "analyze": analyze_msg,
                "export": export_msg,
                "vacancy": vacancy_msg
            },
            "analyses_remaining": analyses_remaining,
            "analyses_used": analyses_used,
            "analyses_limit": analyses_limit,
            "is_unlimited": is_unlimited,
            "reset_date": reset_date
        })

    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in check_limits: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "LIMITS_CHECK_ERROR",
                "message": f"Ошибка при проверке лимитов: {str(e)}"
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

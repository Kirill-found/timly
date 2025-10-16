"""
API endpoints для администраторов
Статистика, управление пользователями и система
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.models.user import User, UserRole
from app.api.auth import get_current_user
from app.services.telegram_service import get_telegram_service
from app.utils.logger import get_logger
from app.utils.response import create_success_response

logger = get_logger(__name__)

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency для проверки прав администратора

    Args:
        current_user: Текущий пользователь

    Returns:
        User объект если пользователь админ

    Raises:
        HTTPException: Если пользователь не админ
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен. Требуются права администратора"
        )
    return current_user


@router.post("/telegram/send-statistics")
async def send_telegram_statistics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Отправить статистику платформы в Telegram

    Требует права администратора.
    Отправляет подробную статистику о пользователях, подписках и платежах.
    """
    try:
        telegram_service = get_telegram_service()

        if not telegram_service.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Telegram сервис не настроен"
            )

        success = await telegram_service.send_statistics(db)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось отправить статистику"
            )

        logger.info(f"Статистика отправлена администратором {current_user.email}")

        return create_success_response(
            data={"message": "Статистика успешно отправлена в Telegram"},
            message="Статистика отправлена"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при отправке статистики: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.get("/statistics")
async def get_statistics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Получить статистику платформы в формате JSON

    Требует права администратора.
    Возвращает подробную статистику без отправки в Telegram.
    """
    from app.models.user import User
    from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus, PlanType
    from app.models.payment import Payment, PaymentStatus
    from sqlalchemy import func, and_
    from datetime import datetime, timedelta

    try:
        # Общая статистика пользователей
        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        users_with_hh_token = db.query(func.count(User.id)).filter(
            User.token_verified == True
        ).scalar() or 0

        # Статистика по подпискам
        subscription_stats = db.query(
            SubscriptionPlan.plan_type,
            func.count(Subscription.id).label('count')
        ).join(
            Subscription, Subscription.plan_id == SubscriptionPlan.id
        ).filter(
            Subscription.status == SubscriptionStatus.active
        ).group_by(SubscriptionPlan.plan_type).all()

        plan_counts = {
            PlanType.free.value: 0,
            PlanType.starter.value: 0,
            PlanType.professional.value: 0,
            PlanType.enterprise.value: 0
        }

        for plan_type, count in subscription_stats:
            plan_counts[plan_type.value] = count

        users_without_subscription = total_users - sum(plan_counts.values())

        # Статистика платежей
        month_ago = datetime.utcnow() - timedelta(days=30)
        payments_last_month = db.query(func.count(Payment.id)).filter(
            and_(
                Payment.created_at >= month_ago,
                Payment.yookassa_status == PaymentStatus.succeeded
            )
        ).scalar() or 0

        revenue_last_month = db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.created_at >= month_ago,
                Payment.yookassa_status == PaymentStatus.succeeded
            )
        ).scalar() or 0.0

        # Новые пользователи за последнюю неделю
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_week = db.query(func.count(User.id)).filter(
            User.created_at >= week_ago
        ).scalar() or 0

        statistics = {
            "users": {
                "total": total_users,
                "active": active_users,
                "with_hh_token": users_with_hh_token,
                "new_this_week": new_users_week,
                "without_subscription": users_without_subscription
            },
            "subscriptions": {
                "free": plan_counts[PlanType.free.value],
                "starter": plan_counts[PlanType.starter.value],
                "professional": plan_counts[PlanType.professional.value],
                "enterprise": plan_counts[PlanType.enterprise.value]
            },
            "payments_last_30_days": {
                "count": payments_last_month,
                "revenue": float(revenue_last_month)
            }
        }

        logger.info(f"Статистика запрошена администратором {current_user.email}")

        return create_success_response(
            data=statistics,
            message="Статистика получена"
        )

    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

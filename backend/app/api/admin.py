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
            data={"message": "Статистика успешно отправлена в Telegram"}
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
            data=statistics
        )

    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.get("/users")
async def get_all_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: str = None
):
    """
    Получить список всех пользователей с их подписками

    Требует права администратора.

    Args:
        skip: Количество пропускаемых записей для пагинации
        limit: Максимальное количество записей
        search: Поисковый запрос (по email или company_name)
    """
    from app.models.subscription import Subscription
    from sqlalchemy import or_

    try:
        # Базовый запрос
        query = db.query(User)

        # Поиск
        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.company_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Пагинация
        total = query.count()
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

        # Формирование данных с подписками
        users_data = []
        for user in users:
            # Получаем активную подписку
            active_subscription = db.query(Subscription).filter(
                Subscription.user_id == user.id,
                Subscription.status.in_(['active', 'trial'])
            ).first()

            user_data = {
                "id": str(user.id),
                "email": user.email,
                "company_name": user.company_name,
                "role": user.role.value,
                "is_active": user.is_active,
                "has_hh_token": user.has_hh_token,
                "token_verified": user.token_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "subscription": None
            }

            if active_subscription and active_subscription.plan:
                user_data["subscription"] = {
                    "id": str(active_subscription.id),
                    "plan_type": active_subscription.plan.plan_type.value,
                    "plan_name": active_subscription.plan.name,
                    "status": active_subscription.status.value,
                    "started_at": active_subscription.started_at.isoformat() if active_subscription.started_at else None,
                    "expires_at": active_subscription.expires_at.isoformat() if active_subscription.expires_at else None,
                    "days_remaining": active_subscription.days_remaining,
                    "usage": active_subscription.usage_percentage
                }

            users_data.append(user_data)

        logger.info(f"Список пользователей запрошен администратором {current_user.email}")

        return create_success_response(
            data={
                "users": users_data,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )

    except Exception as e:
        logger.error(f"Ошибка при получении списка пользователей: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.post("/users/{user_id}/subscription")
async def update_user_subscription(
    user_id: str,
    plan_type: str,
    duration_months: int = 1,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Изменить подписку пользователя (создать или обновить)

    Требует права администратора.

    Args:
        user_id: ID пользователя
        plan_type: Тип тарифа (free, starter, professional, enterprise)
        duration_months: Длительность подписки в месяцах
    """
    from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus, PlanType
    from datetime import datetime, timedelta
    import uuid

    try:
        # Проверяем существование пользователя
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        # Проверяем валидность плана
        try:
            plan_type_enum = PlanType(plan_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неверный тип тарифа. Доступные: free, starter, professional, enterprise"
            )

        # Получаем план
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.plan_type == plan_type_enum
        ).first()

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тарифный план не найден"
            )

        # Ищем активную подписку пользователя
        active_subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status.in_([SubscriptionStatus.active, SubscriptionStatus.trial])
        ).first()

        now = datetime.utcnow()
        expires_at = now + timedelta(days=duration_months * 30)

        if active_subscription:
            # Обновляем существующую подписку
            active_subscription.plan_id = plan.id
            active_subscription.status = SubscriptionStatus.active
            active_subscription.expires_at = expires_at
            logger.info(f"Подписка обновлена для пользователя {user.email} на {plan_type}")
        else:
            # Создаём новую подписку
            new_subscription = Subscription(
                id=uuid.uuid4(),
                user_id=uuid.UUID(user_id),
                plan_id=plan.id,
                status=SubscriptionStatus.active,
                started_at=now,
                expires_at=expires_at
            )
            db.add(new_subscription)
            logger.info(f"Создана новая подписка для пользователя {user.email} на {plan_type}")

        db.commit()

        return create_success_response(
            data={
                "message": f"Подписка пользователя успешно {'обновлена' if active_subscription else 'создана'}",
                "user_email": user.email,
                "plan_type": plan_type,
                "expires_at": expires_at.isoformat()
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при обновлении подписки: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

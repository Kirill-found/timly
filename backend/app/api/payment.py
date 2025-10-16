"""
API endpoints для работы с платежами
Создание платежей, webhook от ЮKassa, история платежей
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.payment_service import PaymentService
from app.schemas.base import APIResponse
from app.utils.response import success, bad_request, not_found
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class CreatePaymentRequest(BaseModel):
    """Запрос на создание платежа"""
    plan_type: str  # starter, professional, enterprise
    duration_months: int = 1  # 1 или 12
    return_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "plan_type": "professional",
                "duration_months": 12,
                "return_url": "https://timly-hr.ru/subscription/success"
            }
        }


@router.post("/create", response_model=APIResponse)
async def create_payment(
    request: CreatePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создать платеж для оплаты подписки

    Returns:
        - payment_id: ID платежа в нашей системе
        - confirmation_url: URL для оплаты в ЮKassa
        - amount: Сумма к оплате
    """
    try:
        service = PaymentService(db)

        payment_data = await service.create_payment(
            user_id=str(current_user.id),
            plan_type=request.plan_type,
            duration_months=request.duration_months,
            return_url=request.return_url
        )

        return success(data=payment_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_PLAN",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error creating payment: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "PAYMENT_CREATION_ERROR",
                "message": "Ошибка при создании платежа"
            }
        )


@router.post("/webhook")
async def yookassa_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Webhook для получения уведомлений от ЮKassa

    Этот endpoint будет вызван ЮKassa при изменении статуса платежа
    """
    try:
        # Получаем JSON данные от ЮKassa
        webhook_data = await request.json()

        logger.info(f"Received webhook from YooKassa: {webhook_data.get('event', 'unknown')}")

        service = PaymentService(db)
        success_handled = await service.handle_webhook(webhook_data)

        if success_handled:
            return {"status": "ok"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process webhook"
            )

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/history", response_model=APIResponse)
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить историю платежей текущего пользователя

    Returns:
        Список всех платежей пользователя
    """
    try:
        service = PaymentService(db)
        payments = await service.get_user_payments(str(current_user.id))

        return success(data={"payments": payments})

    except Exception as e:
        logger.error(f"Error fetching payment history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "PAYMENT_HISTORY_ERROR",
                "message": "Ошибка при получении истории платежей"
            }
        )


@router.get("/{payment_id}", response_model=APIResponse)
async def get_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получить информацию о конкретном платеже

    Args:
        payment_id: ID платежа
    """
    try:
        service = PaymentService(db)
        payment = await service.get_payment_by_id(payment_id)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "PAYMENT_NOT_FOUND",
                    "message": "Платеж не найден"
                }
            )

        # Проверяем что платеж принадлежит текущему пользователю
        if str(payment.user_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "ACCESS_DENIED",
                    "message": "Нет доступа к этому платежу"
                }
            )

        return success(data={"payment": payment.to_dict()})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payment: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "PAYMENT_FETCH_ERROR",
                "message": "Ошибка при получении платежа"
            }
        )

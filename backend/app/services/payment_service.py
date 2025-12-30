"""
Сервис для работы с платежами через ЮKassa
Создание платежей, обработка webhook'ов, активация подписок
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from yookassa import Configuration, Payment as YooPayment
from yookassa.domain.notification import WebhookNotification

from app.config import settings
from app.models.payment import Payment, PaymentStatus
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus, PlanType
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PaymentService:
    """Сервис для работы с платежами через ЮKassa"""

    def __init__(self, db: Session):
        self.db = db

        # Инициализация ЮKassa (пока с пустыми credentials, позже добавим в .env)
        if hasattr(settings, 'YOOKASSA_SHOP_ID') and hasattr(settings, 'YOOKASSA_SECRET_KEY'):
            Configuration.account_id = settings.YOOKASSA_SHOP_ID
            Configuration.secret_key = settings.YOOKASSA_SECRET_KEY
            logger.info("ЮKassa configured successfully")
        else:
            logger.warning("ЮKassa credentials not found in settings")

    async def create_payment(
        self,
        user_id: str,
        plan_type: str,
        duration_months: int = 1,
        return_url: str = None
    ) -> Dict[str, Any]:
        """
        Создание платежа в ЮKassa

        Args:
            user_id: ID пользователя
            plan_type: Тип тарифа (starter, professional, enterprise)
            duration_months: Длительность (1 или 12 месяцев)
            return_url: URL для возврата после оплаты

        Returns:
            Dict с информацией о платеже и URL для оплаты
        """
        try:
            # Получаем информацию о тарифе
            plan = self.db.query(SubscriptionPlan).filter(
                SubscriptionPlan.plan_type == PlanType[plan_type]
            ).first()

            if not plan:
                raise ValueError(f"План {plan_type} не найден")

            # Вычисляем сумму
            if duration_months == 12:
                amount = plan.price_yearly
                description = f"Подписка {plan.name} на 12 месяцев"
            else:
                amount = plan.price_monthly
                description = f"Подписка {plan.name} на 1 месяц"

            # Validate amount
            if amount <= 0:
                raise ValueError(f"Недопустимая сумма платежа: {amount}. Для бесплатных планов используйте активацию без оплаты.")

            logger.info(f"Creating payment: plan={plan_type}, amount={amount}, duration={duration_months}, return_url={return_url}")

            # Получаем email пользователя для чека
            user = self.db.query(User).filter(User.id == user_id).first()
            user_email = user.email if user else "customer@example.com"

            # Создаем платеж в ЮKassa с чеком (54-ФЗ)
            payment = YooPayment.create({
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url or f"{settings.FRONTEND_URL}/subscription/success"
                },
                "capture": True,
                "description": description,
                "metadata": {
                    "user_id": str(user_id),
                    "plan_type": plan_type,
                    "duration_months": duration_months
                },
                "receipt": {
                    "customer": {
                        "email": user_email
                    },
                    "items": [
                        {
                            "description": description[:128],  # Max 128 chars
                            "quantity": "1.00",
                            "amount": {
                                "value": f"{amount:.2f}",
                                "currency": "RUB"
                            },
                            "vat_code": 1,  # НДС не облагается
                            "payment_subject": "service",
                            "payment_mode": "full_payment"
                        }
                    ]
                }
            })

            # Сохраняем платеж в БД
            db_payment = Payment(
                user_id=user_id,
                yookassa_payment_id=payment.id,
                yookassa_status=PaymentStatus.pending,
                amount=amount,
                currency="RUB",
                description=description,
                plan_type=plan_type,
                duration_months=duration_months
            )
            self.db.add(db_payment)
            self.db.commit()
            self.db.refresh(db_payment)

            logger.info(f"Payment created: {payment.id} for user {user_id}, amount {amount} RUB")

            return {
                "payment_id": str(db_payment.id),
                "yookassa_payment_id": payment.id,
                "confirmation_url": payment.confirmation.confirmation_url,
                "amount": amount,
                "currency": "RUB",
                "status": "pending"
            }

        except Exception as e:
            # Try to get more details from YooKassa error
            error_details = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = f"{e} - Response: {e.response.text}"
                except:
                    pass
            logger.error(f"Error creating payment: {error_details}", exc_info=True)
            raise

    async def handle_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Обработка webhook от ЮKassa

        Args:
            webhook_data: Данные от ЮKassa

        Returns:
            True если обработка успешна
        """
        try:
            notification = WebhookNotification(webhook_data)
            payment_info = notification.object

            logger.info(f"Webhook received for payment {payment_info.id}, status: {payment_info.status}")

            # Находим платеж в БД
            payment = self.db.query(Payment).filter(
                Payment.yookassa_payment_id == payment_info.id
            ).first()

            if not payment:
                logger.error(f"Payment {payment_info.id} not found in database")
                return False

            # Обновляем статус платежа
            old_status = payment.yookassa_status
            payment.yookassa_status = PaymentStatus[payment_info.status]

            if payment_info.status == "succeeded" and old_status != PaymentStatus.succeeded:
                payment.paid_at = datetime.utcnow()

                # Активируем/продлеваем подписку
                await self._activate_subscription(payment)

                logger.info(f"Payment {payment_info.id} succeeded, subscription activated for user {payment.user_id}")

                # Отправляем уведомление в Telegram
                try:
                    from app.services.telegram_service import notify_new_payment
                    user = self.db.query(User).filter(User.id == payment.user_id).first()
                    if user:
                        await notify_new_payment(
                            user.email,
                            payment.amount,
                            payment.plan_type,
                            payment.duration_months
                        )
                except Exception as e:
                    logger.error(f"Не удалось отправить Telegram уведомление о платеже: {e}")

            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error handling webhook: {e}", exc_info=True)
            self.db.rollback()
            return False

    async def _activate_subscription(self, payment: Payment):
        """
        Активация или продление подписки после успешной оплаты

        Args:
            payment: Объект платежа
        """
        try:
            # Получаем или создаем подписку пользователя
            subscription = self.db.query(Subscription).filter(
                Subscription.user_id == payment.user_id
            ).order_by(Subscription.created_at.desc()).first()

            # Получаем план
            plan = self.db.query(SubscriptionPlan).filter(
                SubscriptionPlan.plan_type == PlanType[payment.plan_type]
            ).first()

            if not plan:
                raise ValueError(f"Plan {payment.plan_type} not found")

            # Вычисляем дату окончания
            if subscription and subscription.expires_at and subscription.is_active:
                # Продлеваем существующую активную подписку
                new_expires_at = subscription.expires_at + timedelta(days=payment.duration_months * 30)
            else:
                # Создаем новую подписку или активируем истекшую
                new_expires_at = datetime.utcnow() + timedelta(days=payment.duration_months * 30)

            if subscription:
                # Обновляем существующую подписку
                subscription.plan_id = plan.id
                subscription.status = SubscriptionStatus.active
                subscription.expires_at = new_expires_at
                subscription.started_at = datetime.utcnow()
                logger.info(f"Subscription updated for user {payment.user_id}")
            else:
                # Создаем новую подписку
                subscription = Subscription(
                    user_id=payment.user_id,
                    plan_id=plan.id,
                    status=SubscriptionStatus.active,
                    started_at=datetime.utcnow(),
                    expires_at=new_expires_at
                )
                self.db.add(subscription)
                logger.info(f"New subscription created for user {payment.user_id}")

            # Связываем платеж с подпиской
            payment.subscription_id = subscription.id

            self.db.commit()

        except Exception as e:
            logger.error(f"Error activating subscription: {e}", exc_info=True)
            raise

    async def get_user_payments(self, user_id: str) -> list:
        """
        Получить историю платежей пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Список платежей
        """
        payments = self.db.query(Payment).filter(
            Payment.user_id == user_id
        ).order_by(Payment.created_at.desc()).all()

        return [payment.to_dict() for payment in payments]

    async def get_payment_by_id(self, payment_id: str) -> Optional[Payment]:
        """
        Получить платеж по ID

        Args:
            payment_id: ID платежа

        Returns:
            Объект платежа или None
        """
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User, Transaction, Achievement, UserAchievement, Payment, GameStats, DiceValueMapping, PendingPayout
from datetime import datetime, timedelta
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с базой данных"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(bind=self.engine)
        self.session: Session = SessionLocal()
        logger.info("Database initialized successfully")

    # ==================== USER METHODS ====================

    def get_or_create_user(self, user_id: int, username: str = None,
                          first_name: str = None, last_name: str = None) -> User:
        """Получить или создать пользователя"""
        user = self.session.query(User).filter_by(user_id=user_id).first()

        if not user:
            user = User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                balance=1000  # Начальный баланс
            )
            self.session.add(user)
            self.session.commit()
            logger.info(f"New user created: {user_id} (@{username})")

        return user

    def get_user(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return self.session.query(User).filter_by(user_id=user_id).first()

    def update_balance(self, user_id: int, amount: int) -> User:
        """Обновить баланс пользователя"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        user.balance += amount

        # Обновляем статистику
        if amount < 0:
            user.total_wagered += abs(amount)
            user.total_spins += 1
            user.last_spin_at = datetime.utcnow()
        elif amount > 0:
            user.total_won += amount
            if amount > user.biggest_win:
                user.biggest_win = amount

        self.session.commit()
        return user

    def ban_user(self, user_id: int, reason: str = None):
        """Заблокировать пользователя"""
        user = self.get_user(user_id)
        if user:
            user.is_banned = True
            user.ban_reason = reason
            self.session.commit()
            logger.info(f"User {user_id} banned: {reason}")

    def unban_user(self, user_id: int):
        """Разблокировать пользователя"""
        user = self.get_user(user_id)
        if user:
            user.is_banned = False
            user.ban_reason = None
            user.strikes = 0  # Сбрасываем страйки при разбане
            self.session.commit()
            logger.info(f"User {user_id} unbanned")

    def is_user_banned(self, user_id: int) -> bool:
        """Проверить, заблокирован ли пользователь"""
        user = self.get_user(user_id)
        return user.is_banned if user else False

    def add_strike(self, user_id: int) -> int:
        """
        Добавить страйк пользователю

        Returns:
            int: Текущее количество страйков
        """
        user = self.get_user(user_id)
        if user:
            user.strikes += 1
            user.last_strike_at = datetime.utcnow()
            self.session.commit()
            logger.info(f"Strike added to user {user_id}. Total: {user.strikes}")
            return user.strikes
        return 0

    def clear_strikes(self, user_id: int):
        """Очистить страйки пользователя"""
        user = self.get_user(user_id)
        if user:
            user.strikes = 0
            user.last_strike_at = None
            self.session.commit()
            logger.info(f"Strikes cleared for user {user_id}")

    # ==================== TRANSACTION METHODS ====================

    def log_transaction(self, user_id: int, transaction_type: str, amount: int,
                       dice_value: int = None, combination: str = None,
                       telegram_payment_id: str = None, telegram_stars_amount: int = None,
                       description: str = None) -> Transaction:
        """Логировать транзакцию"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        balance_before = user.balance - amount

        transaction = Transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=user.balance,
            dice_value=dice_value,
            combination=combination,
            telegram_payment_id=telegram_payment_id,
            telegram_stars_amount=telegram_stars_amount,
            description=description
        )

        self.session.add(transaction)
        self.session.commit()
        return transaction

    def get_user_transactions(self, user_id: int, limit: int = 50) -> List[Transaction]:
        """Получить транзакции пользователя"""
        return self.session.query(Transaction)\
            .filter_by(user_id=user_id)\
            .order_by(desc(Transaction.timestamp))\
            .limit(limit)\
            .all()

    # ==================== ACHIEVEMENT METHODS ====================

    def create_achievement(self, code: str, title: str, description: str,
                          icon: str, reward: int, requirement_description: str) -> Achievement:
        """Создать достижение"""
        achievement = Achievement(
            code=code,
            title=title,
            description=description,
            icon=icon,
            reward=reward,
            requirement_description=requirement_description
        )
        self.session.add(achievement)
        self.session.commit()
        return achievement

    def get_achievement_by_code(self, code: str) -> Optional[Achievement]:
        """Получить достижение по коду"""
        return self.session.query(Achievement).filter_by(code=code).first()

    def get_all_achievements(self) -> List[Achievement]:
        """Получить все активные достижения"""
        return self.session.query(Achievement).filter_by(is_active=True).all()

    def unlock_achievement(self, user_id: int, achievement_code: str) -> Optional[UserAchievement]:
        """Разблокировать достижение для пользователя"""
        achievement = self.get_achievement_by_code(achievement_code)
        if not achievement:
            logger.warning(f"Achievement {achievement_code} not found")
            return None

        # Проверяем, не разблокировано ли уже
        existing = self.session.query(UserAchievement)\
            .filter_by(user_id=user_id, achievement_id=achievement.id)\
            .first()

        if existing:
            return None  # Уже разблокировано

        # Создаём запись
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement.id
        )
        self.session.add(user_achievement)

        # Увеличиваем счётчик достижений пользователя
        user = self.get_user(user_id)
        if user:
            user.achievements_unlocked += 1

        # Начисляем награду
        if achievement.reward > 0:
            self.update_balance(user_id, achievement.reward)
            self.log_transaction(
                user_id=user_id,
                transaction_type='achievement',
                amount=achievement.reward,
                description=f"Награда за достижение: {achievement.title}"
            )

        self.session.commit()
        logger.info(f"Achievement {achievement_code} unlocked for user {user_id}")
        return user_achievement

    def get_user_achievements(self, user_id: int) -> List[UserAchievement]:
        """Получить достижения пользователя"""
        return self.session.query(UserAchievement)\
            .filter_by(user_id=user_id)\
            .all()

    def has_achievement(self, user_id: int, achievement_code: str) -> bool:
        """Проверить, есть ли у пользователя достижение"""
        achievement = self.get_achievement_by_code(achievement_code)
        if not achievement:
            return False

        return self.session.query(UserAchievement)\
            .filter_by(user_id=user_id, achievement_id=achievement.id)\
            .first() is not None

    # ==================== PAYMENT METHODS ====================

    def create_payment(self, user_id: int, telegram_payment_charge_id: str,
                      telegram_stars_amount: int, game_stars_amount: int,
                      provider_payment_charge_id: str = None) -> Payment:
        """Создать запись о платеже"""
        payment = Payment(
            user_id=user_id,
            telegram_payment_charge_id=telegram_payment_charge_id,
            provider_payment_charge_id=provider_payment_charge_id,
            telegram_stars_amount=telegram_stars_amount,
            game_stars_amount=game_stars_amount,
            status='pending'
        )
        self.session.add(payment)
        self.session.commit()
        return payment

    def complete_payment(self, payment_id: int) -> Optional[Payment]:
        """Завершить платёж"""
        payment = self.session.query(Payment).filter_by(id=payment_id).first()
        if payment:
            payment.status = 'completed'
            payment.completed_at = datetime.utcnow()

            # Начисляем звёзды пользователю
            self.update_balance(payment.user_id, payment.game_stars_amount)

            # Логируем транзакцию
            self.log_transaction(
                user_id=payment.user_id,
                transaction_type='purchase',
                amount=payment.game_stars_amount,
                telegram_payment_id=payment.telegram_payment_charge_id,
                telegram_stars_amount=payment.telegram_stars_amount,
                description=f"Покупка {payment.game_stars_amount} звёзд за {payment.telegram_stars_amount} Telegram Stars"
            )

            self.session.commit()
            logger.info(f"Payment {payment_id} completed for user {payment.user_id}")
        return payment

    def get_user_payments(self, user_id: int) -> List[Payment]:
        """Получить платежи пользователя"""
        return self.session.query(Payment)\
            .filter_by(user_id=user_id)\
            .order_by(desc(Payment.timestamp))\
            .all()

    # ==================== STATISTICS METHODS ====================

    def get_user_stats(self, user_id: int) -> dict:
        """Получить статистику пользователя"""
        user = self.get_user(user_id)
        if not user:
            return {}

        return {
            'total_spins': user.total_spins,
            'total_wagered': user.total_wagered,
            'total_won': user.total_won,
            'biggest_win': user.biggest_win,
            'balance': user.balance,
            'achievements': user.achievements_unlocked,
            'profit_loss': user.total_won - user.total_wagered
        }

    def get_top_users(self, limit: int = 10) -> List[User]:
        """Получить топ игроков по балансу"""
        return self.session.query(User)\
            .filter_by(is_banned=False)\
            .order_by(desc(User.balance))\
            .limit(limit)\
            .all()

    def get_global_stats(self) -> dict:
        """Получить глобальную статистику"""
        # Общее количество пользователей
        total_users = self.session.query(func.count(User.user_id)).scalar()

        # Активные пользователи (за последние 24 часа)
        day_ago = datetime.utcnow() - timedelta(days=1)
        active_users = self.session.query(func.count(User.user_id))\
            .filter(User.last_spin_at >= day_ago)\
            .scalar()

        # Новые пользователи (за последние 24 часа)
        new_users = self.session.query(func.count(User.user_id))\
            .filter(User.created_at >= day_ago)\
            .scalar()

        # Общая статистика
        stats = self.session.query(
            func.sum(User.total_spins).label('total_spins'),
            func.sum(User.total_wagered).label('total_wagered'),
            func.sum(User.total_won).label('total_won'),
            func.sum(User.balance).label('total_balance')
        ).first()

        total_spins = stats.total_spins or 0
        total_wagered = stats.total_wagered or 0
        total_won = stats.total_won or 0
        total_balance = stats.total_balance or 0

        # Расчёт RTP
        actual_rtp = (total_won / total_wagered * 100) if total_wagered > 0 else 0

        # Прибыль "казино"
        house_profit = total_wagered - total_won

        # Платежи
        payments_stats = self.session.query(
            func.count(Payment.id).label('count'),
            func.sum(Payment.telegram_stars_amount).label('total_stars'),
            func.sum(Payment.game_stars_amount).label('total_game_stars')
        ).filter_by(status='completed').first()

        return {
            'total_users': total_users,
            'active_users': active_users,
            'new_users': new_users,
            'total_spins': total_spins,
            'total_wagered': total_wagered,
            'total_won': total_won,
            'total_balance': total_balance,
            'actual_rtp': actual_rtp,
            'house_profit': house_profit,
            'total_purchases': payments_stats.count or 0,
            'total_telegram_stars_received': payments_stats.total_stars or 0,
            'total_game_stars_sold': payments_stats.total_game_stars or 0
        }

    # ==================== DICE VALUE MAPPING METHODS ====================

    def record_dice_value(self, dice_value: int, combination: str = None,
                         is_win: bool = False, payout_multiplier: float = 0.0):
        """Записать появление dice_value (для тестирования)"""
        mapping = self.session.query(DiceValueMapping)\
            .filter_by(dice_value=dice_value).first()

        if mapping:
            mapping.occurrence_count += 1
            mapping.last_seen = datetime.utcnow()
        else:
            mapping = DiceValueMapping(
                dice_value=dice_value,
                combination=combination,
                is_win=is_win,
                payout_multiplier=payout_multiplier,
                occurrence_count=1,
                last_seen=datetime.utcnow()
            )
            self.session.add(mapping)

        self.session.commit()

    def get_dice_statistics(self) -> List[DiceValueMapping]:
        """Получить статистику по dice_value"""
        return self.session.query(DiceValueMapping)\
            .order_by(DiceValueMapping.dice_value)\
            .all()

    def close(self):
        """Закрыть соединение с БД"""
        self.session.close()

    # ==================== PAYOUT METHODS ====================

    def create_pending_payout(self, user_id: int, username: str, amount: int,
                            dice_value: int = None, combination: str = None,
                            transaction_id: int = None) -> PendingPayout:
        """Создать запись о выигрыше для выплаты"""
        payout = PendingPayout(
            user_id=user_id,
            username=username,
            amount=amount,
            dice_value=dice_value,
            combination=combination,
            transaction_id=transaction_id,
            status='pending'
        )
        self.session.add(payout)
        self.session.commit()
        logger.info(f"Created pending payout: user={user_id}, amount={amount}")
        return payout

    def get_pending_payouts(self, status: str = 'pending') -> List[PendingPayout]:
        """Получить все невыплаченные выигрыши"""
        return self.session.query(PendingPayout)\
            .filter_by(status=status)\
            .order_by(PendingPayout.created_at.asc())\
            .all()

    def mark_payout_paid(self, payout_id: int, admin_note: str = None):
        """Отметить выплату как оплаченную"""
        payout = self.session.query(PendingPayout).filter_by(id=payout_id).first()
        if payout:
            payout.status = 'paid'
            payout.paid_at = datetime.utcnow()
            if admin_note:
                payout.admin_note = admin_note
            self.session.commit()
            logger.info(f"Payout {payout_id} marked as paid")

    def mark_payout_failed(self, payout_id: int, error: str):
        """Отметить выплату как неудачную"""
        payout = self.session.query(PendingPayout).filter_by(id=payout_id).first()
        if payout:
            payout.status = 'failed'
            payout.last_error = error
            payout.attempts += 1
            self.session.commit()
            logger.error(f"Payout {payout_id} failed: {error}")

    def get_payout_stats(self) -> dict:
        """Получить статистику по выплатам"""
        pending = self.session.query(func.count(PendingPayout.id), func.sum(PendingPayout.amount))\
            .filter_by(status='pending').first()

        paid = self.session.query(func.count(PendingPayout.id), func.sum(PendingPayout.amount))\
            .filter_by(status='paid').first()

        return {
            'pending_count': pending[0] or 0,
            'pending_amount': pending[1] or 0,
            'paid_count': paid[0] or 0,
            'paid_amount': paid[1] or 0
        }

    # TON Wallet методы
    def set_user_ton_address(self, user_id: int, ton_address: str, verified: bool = False):
        """Установить TON адрес пользователя"""
        user = self.get_user(user_id)
        if user:
            user.ton_address = ton_address
            user.ton_address_verified = verified
            self.session.commit()
            logger.info(f"Set TON address for user {user_id}: {ton_address}")
        else:
            logger.warning(f"User {user_id} not found when setting TON address")

    def get_user_ton_address(self, user_id: int) -> str:
        """Получить TON адрес пользователя"""
        user = self.get_user(user_id)
        return user.ton_address if user else None

    def verify_user_ton_address(self, user_id: int):
        """Подтвердить TON адрес пользователя"""
        user = self.get_user(user_id)
        if user:
            user.ton_address_verified = True
            self.session.commit()
            logger.info(f"Verified TON address for user {user_id}")

    def create_ton_transaction(
        self,
        user_id: int,
        amount_stars: int,
        amount_ton: float,
        destination: str,
        transaction_hash: str = None,
        status: str = 'pending'
    ) -> Transaction:
        """Создать запись о TON транзакции"""
        transaction = Transaction(
            user_id=user_id,
            transaction_type='ton_payout',
            amount=-amount_stars,  # Списание stars
            ton_amount=amount_ton,
            ton_destination=destination,
            ton_transaction_hash=transaction_hash,
            ton_status=status,
            description=f"TON payout: {amount_stars} stars → {amount_ton} TON"
        )
        self.session.add(transaction)
        self.session.commit()
        logger.info(f"Created TON transaction: user={user_id}, amount={amount_ton} TON")
        return transaction

    def update_ton_transaction_status(
        self,
        transaction_id: int,
        status: str,
        transaction_hash: str = None
    ):
        """Обновить статус TON транзакции"""
        transaction = self.session.query(Transaction).filter_by(id=transaction_id).first()
        if transaction:
            transaction.ton_status = status
            if transaction_hash:
                transaction.ton_transaction_hash = transaction_hash
            self.session.commit()
            logger.info(f"Updated TON transaction {transaction_id}: status={status}")

    def get_pending_ton_payouts(self) -> list:
        """Получить все незавершенные TON выплаты"""
        return self.session.query(Transaction)\
            .filter_by(transaction_type='ton_payout', ton_status='pending')\
            .order_by(Transaction.timestamp.asc())\
            .all()

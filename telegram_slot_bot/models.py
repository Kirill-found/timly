from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)  # Telegram user ID
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    balance = Column(Integer, default=1000)

    # Статистика игр
    total_spins = Column(Integer, default=0)
    total_wagered = Column(Integer, default=0)
    total_won = Column(Integer, default=0)
    biggest_win = Column(Integer, default=0)

    # Достижения
    achievements_unlocked = Column(Integer, default=0)

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    last_spin_at = Column(DateTime)
    last_bonus_at = Column(DateTime)

    # Блокировка и страйки
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(Text)
    strikes = Column(Integer, default=0)  # Количество страйков (3 = бан)
    last_strike_at = Column(DateTime)  # Время последнего страйка

    # TON кошелек для выплат
    ton_address = Column(String(255))  # TON адрес пользователя для автоматических выплат
    ton_address_verified = Column(Boolean, default=False)  # Подтвержден ли адрес

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username}, balance={self.balance})>"


class Transaction(Base):
    """Модель транзакций"""
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)

    # Тип транзакции: 'spin', 'win', 'purchase', 'bonus', 'achievement'
    transaction_type = Column(String(50))

    amount = Column(Integer)  # Положительное для пополнения, отрицательное для списания
    balance_before = Column(Integer)
    balance_after = Column(Integer)

    # Данные о спине
    dice_value = Column(Integer)
    combination = Column(String(50))

    # Данные о покупке
    telegram_payment_id = Column(String(255))
    telegram_stars_amount = Column(Integer)

    # TON транзакция
    ton_transaction_hash = Column(String(255))  # Hash TON транзакции
    ton_amount = Column(Float)  # Сумма в TON
    ton_destination = Column(String(255))  # Адрес получателя
    ton_status = Column(String(50))  # pending, confirmed, failed

    # Описание
    description = Column(Text)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, type={self.transaction_type}, amount={self.amount})>"


class Achievement(Base):
    """Модель достижений"""
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100), unique=True, nullable=False)  # Уникальный код достижения
    title = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(10))  # Emoji
    reward = Column(Integer, default=0)  # Награда в звёздах

    # Условия получения (для отображения)
    requirement_description = Column(Text)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Achievement(code={self.code}, title={self.title}, reward={self.reward})>"


class UserAchievement(Base):
    """Модель связи пользователь-достижение"""
    __tablename__ = 'user_achievements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)
    achievement_id = Column(Integer, index=True)

    unlocked_at = Column(DateTime, default=datetime.utcnow)
    is_notified = Column(Boolean, default=False)  # Было ли отправлено уведомление

    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id})>"


class Payment(Base):
    """Модель платежей через Telegram Stars"""
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)

    # Данные платежа
    telegram_payment_charge_id = Column(String(255), unique=True)
    provider_payment_charge_id = Column(String(255))

    # Суммы
    telegram_stars_amount = Column(Integer)  # Сколько Telegram Stars заплатил пользователь
    game_stars_amount = Column(Integer)  # Сколько игровых звёзд получил

    # Статус
    status = Column(String(50), default='pending')  # pending, completed, failed, refunded

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)

    def __repr__(self):
        return f"<Payment(id={self.id}, user_id={self.user_id}, stars={self.telegram_stars_amount}, status={self.status})>"


class GameStats(Base):
    """Модель глобальной статистики игры (для админки)"""
    __tablename__ = 'game_stats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)

    # Статистика за период
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)

    total_spins = Column(Integer, default=0)
    total_wagered = Column(Integer, default=0)
    total_won = Column(Integer, default=0)

    # Финансовая статистика
    total_purchases = Column(Integer, default=0)
    total_telegram_stars_received = Column(Integer, default=0)
    total_game_stars_sold = Column(Integer, default=0)

    # RTP
    actual_rtp = Column(Float)
    house_profit = Column(Integer, default=0)

    def __repr__(self):
        return f"<GameStats(date={self.date}, users={self.total_users}, spins={self.total_spins})>"


class DiceValueMapping(Base):
    """Модель для хранения соответствия dice_value и комбинаций (для тестирования)"""
    __tablename__ = 'dice_value_mappings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    dice_value = Column(Integer, unique=True, nullable=False)
    combination = Column(String(50))  # Описание комбинации
    is_win = Column(Boolean, default=False)
    payout_multiplier = Column(Float, default=0.0)

    # Статистика появления (для расчёта вероятностей)
    occurrence_count = Column(Integer, default=0)

    last_seen = Column(DateTime)

    def __repr__(self):
        return f"<DiceValueMapping(dice_value={self.dice_value}, combination={self.combination})>"


class PendingPayout(Base):
    """Модель для отслеживания выплат выигрышей"""
    __tablename__ = 'pending_payouts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(255))

    # Детали выигрыша
    amount = Column(Integer, nullable=False)  # Сумма выплаты в звёздах
    dice_value = Column(Integer)
    combination = Column(String(50))

    # Статус выплаты
    status = Column(String(20), default='pending')  # pending, paid, failed

    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime)

    # Дополнительная информация
    attempts = Column(Integer, default=0)
    last_error = Column(Text)
    transaction_id = Column(Integer)  # Ссылка на транзакцию
    admin_note = Column(Text)  # Заметка администратора

    def __repr__(self):
        return f"<PendingPayout(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"

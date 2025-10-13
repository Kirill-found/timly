"""
Скрипт для обновления тестового пользователя test@timly.ru
Устанавливает роль admin и подписку Enterprise
"""
import sys
import os
from datetime import datetime, timedelta

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User
from app.models.subscription import SubscriptionPlan, Subscription, PlanType, SubscriptionStatus


def upgrade_test_user(db: Session):
    """Обновление тестового пользователя до администратора с Enterprise планом"""

    print("=" * 80)
    print("Обновление тестового пользователя test@timly.ru")
    print("=" * 80)

    # 1. Найти пользователя
    user = db.query(User).filter(User.email == "test@timly.ru").first()

    if not user:
        print("\nОшибка: Пользователь test@timly.ru не найден!")
        print("Создайте пользователя через регистрацию или используйте другой email.")
        return False

    print(f"\nНайден пользователь:")
    print(f"  ID: {user.id}")
    print(f"  Email: {user.email}")
    print(f"  Текущая роль: {user.role}")
    print(f"  Активен: {user.is_active}")

    # 2. Обновить роль на admin
    old_role = user.role
    user.role = "admin"
    print(f"\nОбновление роли: {old_role} -> admin")

    # 3. Найти Enterprise план
    enterprise_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.plan_type == PlanType.enterprise
    ).first()

    if not enterprise_plan:
        print("\nОшибка: Enterprise план не найден в базе данных!")
        print("Сначала запустите app/scripts/init_subscription_plans.py")
        return False

    print(f"\nНайден Enterprise план:")
    print(f"  ID: {enterprise_plan.id}")
    print(f"  Название: {enterprise_plan.name}")
    print(f"  Макс. вакансий: {enterprise_plan.max_active_vacancies}")
    print(f"  Макс. анализов/месяц: {enterprise_plan.max_analyses_per_month}")
    print(f"  Макс. экспортов/месяц: {enterprise_plan.max_export_per_month}")

    # 4. Проверить существующую подписку
    existing_subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id
    ).first()

    if existing_subscription:
        print(f"\nОбновление существующей подписки:")
        print(f"  Старый план: {existing_subscription.plan.name}")

        # Обновляем существующую подписку
        existing_subscription.plan_id = enterprise_plan.id
        existing_subscription.status = SubscriptionStatus.active
        existing_subscription.analyses_used_this_month = 0
        existing_subscription.exports_used_this_month = 0
        existing_subscription.started_at = datetime.utcnow()
        existing_subscription.expires_at = datetime.utcnow() + timedelta(days=365)  # 1 год
        existing_subscription.cancelled_at = None
        existing_subscription.last_reset_at = datetime.utcnow()

        print(f"  Новый план: {enterprise_plan.name}")
        print(f"  Статус: {existing_subscription.status.value}")
        print(f"  Период действия: до {existing_subscription.expires_at.strftime('%Y-%m-%d')}")
    else:
        # Создаем новую подписку
        print(f"\nСоздание новой Enterprise подписки:")

        new_subscription = Subscription(
            user_id=user.id,
            plan_id=enterprise_plan.id,
            status=SubscriptionStatus.active,
            analyses_used_this_month=0,
            exports_used_this_month=0,
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=365),  # 1 год
            last_reset_at=datetime.utcnow()
        )
        db.add(new_subscription)

        print(f"  План: {enterprise_plan.name}")
        print(f"  Статус: active")
        print(f"  Период действия: до {new_subscription.expires_at.strftime('%Y-%m-%d')}")

    # 5. Сохранить изменения
    try:
        db.commit()
        print("\n" + "=" * 80)
        print("Успешно! Пользователь test@timly.ru обновлен!")
        print("=" * 80)
        print("\nТеперь у пользователя есть:")
        print("  - Роль: admin")
        print("  - Подписка: Enterprise")
        print("  - Неограниченные вакансии")
        print("  - Неограниченные анализы")
        print("  - Неограниченные экспорты")
        print("  - Все премиум-функции")
        print("\nВойдите в систему заново, чтобы изменения вступили в силу.")
        print("=" * 80)
        return True
    except Exception as e:
        db.rollback()
        print(f"\nОшибка при сохранении: {e}")
        return False


def main():
    """Главная функция"""
    print("\nИнициализация подключения к базе данных...")

    db = SessionLocal()
    try:
        success = upgrade_test_user(db)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

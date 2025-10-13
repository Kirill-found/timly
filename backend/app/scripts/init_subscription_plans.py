"""
Скрипт инициализации тарифных планов
Создаёт базовые тарифы в базе данных
"""
import sys
import os

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.subscription import SubscriptionPlan, PlanType
import json


def create_default_plans(db: Session):
    """
    Создание стандартных тарифных планов
    """

    # Проверяем, есть ли уже планы
    existing_plans = db.query(SubscriptionPlan).count()
    if existing_plans > 0:
        print(f"Тарифные планы уже существуют ({existing_plans} шт.)")
        return

    plans_data = [
        {
            "plan_type": PlanType.free,
            "name": "Free",
            "description": "Бесплатный тариф для знакомства с платформой",
            "price_monthly": 0.0,
            "price_yearly": 0.0,
            "currency": "RUB",
            "max_active_vacancies": 1,
            "max_analyses_per_month": 20,
            "max_export_per_month": 5,
            "features": json.dumps({
                "basic_analysis": True,
                "email_support": True,
                "export_excel": True,
                "api_access": False,
                "priority_support": False,
                "custom_reports": False,
                "team_collaboration": False
            }),
            "display_order": 1,
            "is_active": True
        },
        {
            "plan_type": PlanType.starter,
            "name": "Starter",
            "description": "Идеальный вариант для небольших компаний и стартапов",
            "price_monthly": 2990.0,
            "price_yearly": 29900.0,  # ~16% скидка
            "currency": "RUB",
            "max_active_vacancies": 5,
            "max_analyses_per_month": 200,
            "max_export_per_month": 50,
            "features": json.dumps({
                "basic_analysis": True,
                "email_support": True,
                "export_excel": True,
                "api_access": False,
                "priority_support": False,
                "custom_reports": False,
                "team_collaboration": False,
                "advanced_filters": True
            }),
            "display_order": 2,
            "is_active": True
        },
        {
            "plan_type": PlanType.professional,
            "name": "Professional",
            "description": "Для профессиональных рекрутеров и HR-команд",
            "price_monthly": 5990.0,
            "price_yearly": 59900.0,  # ~16% скидка
            "currency": "RUB",
            "max_active_vacancies": 20,
            "max_analyses_per_month": 1000,
            "max_export_per_month": 200,
            "features": json.dumps({
                "basic_analysis": True,
                "email_support": True,
                "export_excel": True,
                "api_access": True,
                "priority_support": True,
                "custom_reports": True,
                "team_collaboration": False,
                "advanced_filters": True,
                "bulk_operations": True,
                "webhook_notifications": True
            }),
            "display_order": 3,
            "is_active": True
        },
        {
            "plan_type": PlanType.enterprise,
            "name": "Enterprise",
            "description": "Для крупных компаний с индивидуальными требованиями",
            "price_monthly": 0.0,  # По запросу
            "price_yearly": 0.0,   # По запросу
            "currency": "RUB",
            "max_active_vacancies": 999999,  # Без ограничений
            "max_analyses_per_month": 999999,  # Без ограничений
            "max_export_per_month": 999999,   # Без ограничений
            "features": json.dumps({
                "basic_analysis": True,
                "email_support": True,
                "export_excel": True,
                "api_access": True,
                "priority_support": True,
                "custom_reports": True,
                "team_collaboration": True,
                "advanced_filters": True,
                "bulk_operations": True,
                "webhook_notifications": True,
                "dedicated_manager": True,
                "custom_integrations": True,
                "sla_guarantee": True,
                "onboarding_support": True
            }),
            "display_order": 4,
            "is_active": True
        }
    ]

    created_count = 0
    for plan_data in plans_data:
        plan = SubscriptionPlan(**plan_data)
        db.add(plan)
        db.flush()  # Получаем ID сразу
        created_count += 1
        print(f"Создан тариф: {plan.name} ({plan.plan_type.value})")

    db.commit()
    print(f"\nУспешно создано {created_count} тарифных планов")


def main():
    """Основная функция скрипта"""
    print("Инициализация тарифных планов...\n")

    # Создаём таблицы если их нет
    Base.metadata.create_all(bind=engine)

    # Создаём сессию
    db = SessionLocal()

    try:
        create_default_plans(db)
        print("\nИнициализация завершена успешно!")
    except Exception as e:
        print(f"\nОшибка при инициализации: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

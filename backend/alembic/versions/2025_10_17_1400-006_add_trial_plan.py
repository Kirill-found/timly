"""Add trial subscription plan

Revision ID: 006
Revises: 004
Create Date: 2025-10-17 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    """
    Добавляем все тарифные планы (Trial, Free, Starter, Professional, Enterprise)
    """
    # Trial план
    op.execute(f"""
        INSERT INTO subscription_plans (
            id, plan_type, name, description,
            price_monthly, price_yearly, currency,
            max_active_vacancies, max_analyses_per_month, max_export_per_month,
            features, is_active, display_order
        ) VALUES (
            '{str(uuid.uuid4())}', 'trial', 'Trial',
            'Пробный тариф для новых пользователей',
            0.0, 0.0, 'RUB', 1, 50, 5,
            '{{"trial_period": true, "email_support": true}}', true, 0
        ) ON CONFLICT DO NOTHING;
    """)

    # Free план
    op.execute(f"""
        INSERT INTO subscription_plans (
            id, plan_type, name, description,
            price_monthly, price_yearly, currency,
            max_active_vacancies, max_analyses_per_month, max_export_per_month,
            features, is_active, display_order
        ) VALUES (
            '{str(uuid.uuid4())}', 'free', 'Free',
            'Бесплатный план с ограниченным функционалом',
            0.0, 0.0, 'RUB', 1, 10, 0,
            '{{"basic_features": true}}', true, 1
        ) ON CONFLICT DO NOTHING;
    """)

    # Starter план
    op.execute(f"""
        INSERT INTO subscription_plans (
            id, plan_type, name, description,
            price_monthly, price_yearly, currency,
            max_active_vacancies, max_analyses_per_month, max_export_per_month,
            features, is_active, display_order
        ) VALUES (
            '{str(uuid.uuid4())}', 'starter', 'Starter',
            'Стартовый план для малого бизнеса',
            2999.0, 29990.0, 'RUB', 3, 100, 50,
            '{{"priority_support": true}}', true, 2
        ) ON CONFLICT DO NOTHING;
    """)

    # Professional план
    op.execute(f"""
        INSERT INTO subscription_plans (
            id, plan_type, name, description,
            price_monthly, price_yearly, currency,
            max_active_vacancies, max_analyses_per_month, max_export_per_month,
            features, is_active, display_order
        ) VALUES (
            '{str(uuid.uuid4())}', 'professional', 'Professional',
            'Профессиональный план для растущих компаний',
            5999.0, 59990.0, 'RUB', 10, 500, 200,
            '{{"api_access": true, "priority_support": true}}', true, 3
        ) ON CONFLICT DO NOTHING;
    """)

    # Enterprise план
    op.execute(f"""
        INSERT INTO subscription_plans (
            id, plan_type, name, description,
            price_monthly, price_yearly, currency,
            max_active_vacancies, max_analyses_per_month, max_export_per_month,
            features, is_active, display_order
        ) VALUES (
            '{str(uuid.uuid4())}', 'enterprise', 'Enterprise',
            'Корпоративный план для крупного бизнеса',
            15999.0, 159990.0, 'RUB', -1, -1, -1,
            '{{"unlimited": true, "dedicated_support": true, "api_access": true}}', true, 4
        ) ON CONFLICT DO NOTHING;
    """)


def downgrade():
    """
    Удаляем Trial тарифный план
    """
    op.execute("""
        DELETE FROM subscription_plans WHERE plan_type = 'trial';
    """)

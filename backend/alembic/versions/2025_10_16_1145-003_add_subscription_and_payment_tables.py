"""Add subscription and payment tables

Revision ID: 003
Revises: 002
Create Date: 2025-10-16 11:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Добавление таблиц для системы подписок и платежей
    """

    # Включение расширения для UUID (если еще не включено)
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Создание таблицы subscription_plans
    op.create_table(
        'subscription_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('plan_type', sa.Enum('free', 'starter', 'professional', 'enterprise', name='plantype'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_monthly', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('price_yearly', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='RUB'),
        sa.Column('max_active_vacancies', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('max_analyses_per_month', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('max_export_per_month', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('features', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_plan_type', 'subscription_plans', ['plan_type'], unique=True)

    # Создание таблицы subscriptions
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('active', 'expired', 'cancelled', 'trial', name='subscriptionstatus'), nullable=False, server_default='trial'),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('analyses_used_this_month', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('exports_used_this_month', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_reset_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'])
    op.create_index('ix_subscriptions_plan_id', 'subscriptions', ['plan_id'])
    op.create_index('ix_subscriptions_status', 'subscriptions', ['status'])

    # Создание таблицы usage_logs
    op.create_table(
        'usage_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('vacancy_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action_metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['vacancy_id'], ['vacancies.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_usage_logs_user_id', 'usage_logs', ['user_id'])
    op.create_index('ix_usage_logs_action_type', 'usage_logs', ['action_type'])
    op.create_index('ix_usage_logs_created_at', 'usage_logs', ['created_at'])

    # Создание таблицы payments
    op.create_table(
        'payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('yookassa_payment_id', sa.String(length=255), nullable=False),
        sa.Column('yookassa_status', sa.Enum('pending', 'waiting_for_capture', 'succeeded', 'canceled', name='paymentstatus'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='RUB'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('plan_type', sa.String(length=50), nullable=False),
        sa.Column('duration_months', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('payment_method', sa.Text(), nullable=True),
        sa.Column('payment_metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payments_yookassa_payment_id', 'payments', ['yookassa_payment_id'], unique=True)
    op.create_index('ix_payments_user_id', 'payments', ['user_id'])
    op.create_index('ix_payments_status', 'payments', ['yookassa_status'])
    op.create_index('ix_payments_created_at', 'payments', ['created_at'])


def downgrade() -> None:
    """
    Откат миграции
    """
    op.drop_table('payments')
    op.drop_table('usage_logs')
    op.drop_table('subscriptions')
    op.drop_table('subscription_plans')

    # Удаление enum типов
    op.execute('DROP TYPE IF EXISTS paymentstatus')
    op.execute('DROP TYPE IF EXISTS subscriptionstatus')
    op.execute('DROP TYPE IF EXISTS plantype')

"""Fix schema alignment with TECHNICAL.md

Revision ID: 002
Revises: 001
Create Date: 2025-01-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Исправления для соответствия TECHNICAL.md:
    1. Добавить UNIQUE constraint для (user_id, hh_vacancy_id) в vacancies
    2. Изменить ai_cost_cents INTEGER -> ai_cost_rub NUMERIC(6,2) в analysis_results
    """

    # 1. Добавить UNIQUE constraint для vacancies
    op.create_unique_constraint(
        'uq_user_vacancy',
        'vacancies',
        ['user_id', 'hh_vacancy_id']
    )

    # 2. Изменить тип поля ai_cost в analysis_results
    # Сначала переименуем старое поле
    op.alter_column(
        'analysis_results',
        'ai_cost_cents',
        new_column_name='ai_cost_cents_old',
        existing_type=sa.Integer(),
        existing_nullable=True
    )

    # Добавим новое поле с правильным типом
    op.add_column(
        'analysis_results',
        sa.Column('ai_cost_rub', sa.Numeric(precision=6, scale=2), nullable=True)
    )

    # Мигрируем данные: конвертируем копейки в рубли
    op.execute("""
        UPDATE analysis_results
        SET ai_cost_rub = ROUND(ai_cost_cents_old::numeric / 100, 2)
        WHERE ai_cost_cents_old IS NOT NULL
    """)

    # Удалим старое поле
    op.drop_column('analysis_results', 'ai_cost_cents_old')


def downgrade() -> None:
    """
    Откат изменений
    """

    # Откат изменения типа поля
    op.add_column(
        'analysis_results',
        sa.Column('ai_cost_cents', sa.Integer(), nullable=True)
    )

    # Мигрируем данные обратно: рубли в копейки
    op.execute("""
        UPDATE analysis_results
        SET ai_cost_cents = ROUND(ai_cost_rub * 100)::integer
        WHERE ai_cost_rub IS NOT NULL
    """)

    op.drop_column('analysis_results', 'ai_cost_rub')

    # Откат UNIQUE constraint
    op.drop_constraint('uq_user_vacancy', 'vacancies', type_='unique')

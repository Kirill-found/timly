"""Change analysis arrays from text[] to JSON

Revision ID: 005
Revises: 004
Create Date: 2025-10-17 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    """
    Изменяем типы полей strengths, weaknesses, red_flags с text[] на JSONB
    JSONB более гибкий тип для хранения массивов и быстрее работает с индексами
    """
    # Изменяем тип с text[] на JSONB с сохранением данных
    # PostgreSQL требует двухступенчатую конвертацию: text[] -> text -> jsonb
    op.execute("""
        ALTER TABLE analysis_results
        ALTER COLUMN strengths TYPE JSONB USING array_to_json(strengths)::jsonb;
    """)

    op.execute("""
        ALTER TABLE analysis_results
        ALTER COLUMN weaknesses TYPE JSONB USING array_to_json(weaknesses)::jsonb;
    """)

    op.execute("""
        ALTER TABLE analysis_results
        ALTER COLUMN red_flags TYPE JSONB USING array_to_json(red_flags)::jsonb;
    """)


def downgrade():
    """
    Откат миграции: возвращаем типы обратно в text[]
    """
    op.execute("""
        ALTER TABLE analysis_results
        ALTER COLUMN strengths TYPE TEXT[] USING strengths::text[];
    """)

    op.execute("""
        ALTER TABLE analysis_results
        ALTER COLUMN weaknesses TYPE TEXT[] USING weaknesses::text[];
    """)

    op.execute("""
        ALTER TABLE analysis_results
        ALTER COLUMN red_flags TYPE TEXT[] USING red_flags::text[];
    """)

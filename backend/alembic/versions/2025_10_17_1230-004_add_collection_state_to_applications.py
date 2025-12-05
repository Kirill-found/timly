"""Add collection_id and state to applications

Revision ID: 004
Revises: 003
Create Date: 2025-10-17 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    """
    Добавляем поля collection_id и state в таблицу applications
    Эти поля используются для синхронизации статусов откликов с HeadHunter
    """
    # Добавляем collection_id (response, consider, interview, discard)
    op.add_column('applications', sa.Column('collection_id', sa.String(length=50), nullable=True))
    op.create_index('ix_applications_collection_id', 'applications', ['collection_id'], unique=False)

    # Добавляем state (ID статуса отклика из HH)
    op.add_column('applications', sa.Column('state', sa.String(length=50), nullable=True))
    op.create_index('ix_applications_state', 'applications', ['state'], unique=False)


def downgrade():
    """
    Откат миграции: удаляем добавленные поля
    """
    op.drop_index('ix_applications_state', table_name='applications')
    op.drop_column('applications', 'state')

    op.drop_index('ix_applications_collection_id', table_name='applications')
    op.drop_column('applications', 'collection_id')

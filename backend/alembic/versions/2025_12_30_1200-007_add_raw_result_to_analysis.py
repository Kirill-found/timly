"""Add raw_result field to analysis_results for AI v3.0 data

Revision ID: 007
Revises: 006
Create Date: 2025-12-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    """Add raw_result JSON column for storing full AI response"""
    op.add_column(
        'analysis_results',
        sa.Column('raw_result', JSON, nullable=True)
    )


def downgrade():
    """Remove raw_result column"""
    op.drop_column('analysis_results', 'raw_result')

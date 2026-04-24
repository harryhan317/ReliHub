"""add_feedbacks_table

Revision ID: a1b2c3d4e5f6
Revises: db349918942c
Create Date: 2026-04-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'db349918942c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'feedbacks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('type', sa.Enum('BUG', 'SUGGESTION', 'CONTENT', 'OTHER', name='feedbacktype'), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('images', postgresql.JSON(), nullable=True),
        sa.Column('contact', sa.String(length=100), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'RESOLVED', 'CLOSED', name='feedbackstatus'), nullable=True),
        sa.Column('reply', sa.Text(), nullable=True),
        sa.Column('replied_by', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('feedbacks')

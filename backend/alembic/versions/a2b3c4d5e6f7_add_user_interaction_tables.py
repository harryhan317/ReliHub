"""add_user_interaction_tables

Revision ID: a2b3c4d5e6f7
Revises: db349918942c
Create Date: 2026-04-21 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, None] = 'db349918942c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('topics', sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'))

    op.create_table(
        'user_collections',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('target_type', sa.String(length=10), nullable=False),
        sa.Column('target_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_user_collections_user_id', 'user_collections', ['user_id'])
    op.create_index('ix_user_collections_target_type', 'user_collections', ['target_type'])
    op.create_index('ix_user_collections_target_id', 'user_collections', ['target_id'])
    op.create_unique_constraint(
        'uq_user_collections_user_target',
        'user_collections',
        ['user_id', 'target_type', 'target_id'],
    )

    op.create_table(
        'user_likes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('target_type', sa.String(length=10), nullable=False),
        sa.Column('target_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_user_likes_user_id', 'user_likes', ['user_id'])
    op.create_index('ix_user_likes_target_type', 'user_likes', ['target_type'])
    op.create_index('ix_user_likes_target_id', 'user_likes', ['target_id'])
    op.create_unique_constraint(
        'uq_user_likes_user_target',
        'user_likes',
        ['user_id', 'target_type', 'target_id'],
    )

    op.create_table(
        'user_reports',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('target_type', sa.String(length=10), nullable=False),
        sa.Column('target_id', sa.String(length=36), nullable=False),
        sa.Column('reason', sa.String(length=50), nullable=False),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_user_reports_user_id', 'user_reports', ['user_id'])
    op.create_index('ix_user_reports_target_type', 'user_reports', ['target_type'])
    op.create_index('ix_user_reports_target_id', 'user_reports', ['target_id'])

    op.create_table(
        'user_checkins',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('checkin_date', sa.String(length=10), nullable=False),
        sa.Column('reward_beans', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_user_checkins_user_id', 'user_checkins', ['user_id'])
    op.create_index('ix_user_checkins_checkin_date', 'user_checkins', ['checkin_date'])
    op.create_unique_constraint(
        'uq_user_checkins_user_date',
        'user_checkins',
        ['user_id', 'checkin_date'],
    )


def downgrade() -> None:
    op.drop_table('user_checkins')
    op.drop_table('user_reports')
    op.drop_table('user_likes')
    op.drop_table('user_collections')
    op.drop_column('topics', 'like_count')

"""Add AI, Resource, Community, Ledger, Notification tables for Sprint B

Revision ID: dcd94c32d506
Revises: 
Create Date: 2026-04-04 19:54:20.179563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'dcd94c32d506'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types first
    sa.Enum('NORMAL', 'SCANNING', 'ISOLATED', 'SUSPICIOUS', 'BLOCKED', 'DELETED', name='filestatus').create(op.get_bind())
    sa.Enum('ACTIVE', 'SOFT_DELETED', 'PERMANENTLY_DELETED', name='lifecyclestatus').create(op.get_bind())
    sa.Enum('CONVERSATION', 'RESOURCE', 'TOPIC', name='targettype').create(op.get_bind())
    sa.Enum('SCANNING', 'PENDING_REVIEW', 'APPROVED', 'REJECTED', 'APPEALING', 'BLOCKED', name='resourcestatus').create(op.get_bind())
    sa.Enum('NONE', 'ACTIVE', 'RESOLVED', 'REFUNDED', name='bountystatus').create(op.get_bind())
    sa.Enum('NORMAL', 'BLOCKED', 'PENDING', name='topicstatus').create(op.get_bind())
    sa.Enum('GOLD_BEAN', 'BONUS_BEAN', name='pointtype').create(op.get_bind())
    sa.Enum(
        'DOWNLOAD', 'DOWNLOAD_REVENUE', 'DESTRUCTION', 'RECHARGE', 'SYSTEM_GIFT',
        'SHARE_REWARD', 'EARLYBIRD_REWARD', 'SIGN_IN', 'INVITE_REWARD',
        'CONTENT_TOPIC', 'CONTENT_POST', 'CATEGORY_FIRST_POST_REWARD', 'CONTENT_ADOPTED',
        'BOUNTY_LOCK', 'BOUNTY_RELEASE', 'BOUNTY_REFUND', 'FEEDBACK_AWARD',
        name='ordertype'
    ).create(op.get_bind())
    sa.Enum('SYSTEM', 'INTERACTION', 'AUDIT', 'REWARD', 'BROADCAST', name='notificationtype').create(op.get_bind())
    sa.Enum('NORMAL', 'HIGH', name='notificationpriority').create(op.get_bind())

    # Create ai_sessions table
    op.create_table('ai_sessions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), index=True, nullable=True),
        sa.Column('title', sa.String(100), nullable=True),
        sa.Column('model_type', sa.String(50), nullable=False, default='general'),
        sa.Column('system_prompt_version', sa.String(50), nullable=False, default='v1.0'),
        sa.Column('total_tokens', sa.Integer, nullable=False, default=0),
        sa.Column('total_turns', sa.Integer, nullable=False, default=0),
        sa.Column('max_turns', sa.Integer, nullable=False, default=50),
        sa.Column('max_tokens', sa.Integer, nullable=False, default=50000),
        sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_created', 'ai_sessions', ['user_id', 'created_at'])

    # Create ai_messages table
    op.create_table('ai_messages',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('session_id', sa.String(36), index=True, nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('token_count', sa.Integer, nullable=False, default=0),
        sa.Column('has_attachment', sa.Boolean, nullable=False, default=False),
        sa.Column('attachment_ids', sa.String(500), nullable=True),
        sa.Column('feedback_type', sa.String(20), nullable=True),
        sa.Column('feedback_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_session_created', 'ai_messages', ['session_id', 'created_at'])

    # Create file_meta table
    op.create_table('file_meta',
        sa.Column('file_uuid', sa.String(36), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=False),
        sa.Column('oss_path', sa.String(1024), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('ref_counts', sa.Integer, nullable=False, default=1),
        sa.Column('status', sa.Enum('NORMAL', 'SCANNING', 'ISOLATED', 'SUSPICIOUS', 'BLOCKED', 'DELETED', name='filestatus'), nullable=False, default='SCANNING'),
        sa.Column('lifecycle_status', sa.Enum('ACTIVE', 'SOFT_DELETED', 'PERMANENTLY_DELETED', name='lifecyclestatus'), nullable=False, default='ACTIVE'),
        sa.Column('uploader_uid', sa.String(36), index=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id', name='file_meta_pkey')
    )
    op.create_index(op.f('ix_file_meta_file_hash'), 'file_meta', ['file_hash'], unique=True)
    op.create_index(op.f('ix_file_meta_status'), 'file_meta', ['status'])
    op.create_index(op.f('ix_file_meta_lifecycle_status'), 'file_meta', ['lifecycle_status'])

    # Create file_usage table
    op.create_table('file_usage',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('file_uuid', sa.String(36), index=True, nullable=False),
        sa.Column('target_id', sa.String(36), index=True, nullable=False),
        sa.Column('target_type', sa.Enum('CONVERSATION', 'RESOURCE', 'TOPIC', name='targettype'), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['file_uuid'], ['file_meta.file_uuid'])
    )

    # Create resources table
    op.create_table('resources',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('uploader_id', sa.String(36), index=True, nullable=False),
        sa.Column('title', sa.String(255), index=True, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category_id', sa.Integer, nullable=False),
        sa.Column('tags', sa.String(500), nullable=True),
        sa.Column('price', sa.Integer, nullable=False, default=5),
        sa.Column('file_uuid', sa.String(36), nullable=False),
        sa.Column('view_count', sa.Integer, nullable=False, default=0),
        sa.Column('download_count', sa.Integer, nullable=False, default=0),
        sa.Column('like_count', sa.Integer, nullable=False, default=0),
        sa.Column('dislike_count', sa.Integer, nullable=False, default=0),
        sa.Column('heat_score', sa.Float, nullable=False, default=0.0),
        sa.Column('is_seed', sa.Boolean, nullable=False, default=False),
        sa.Column('status', sa.Enum('SCANNING', 'PENDING_REVIEW', 'APPROVED', 'REJECTED', 'APPEALING', 'BLOCKED', name='resourcestatus'), nullable=False, default='SCANNING'),
        sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),
        sa.Column('anonymized_user_hash', sa.String(64), index=True, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resources_heat_score'), 'resources', ['heat_score'])

    # Create resource_previews table
    op.create_table('resource_previews',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('resource_id', sa.String(36), index=True, nullable=False),
        sa.Column('preview_url', sa.String(1024), nullable=False),
        sa.Column('page_number', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create topics table
    op.create_table('topics',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('author_id', sa.String(36), index=True, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('category_id', sa.Integer, nullable=False),
        sa.Column('bounty_amount', sa.Integer, nullable=False, default=0),
        sa.Column('bounty_status', sa.Enum('NONE', 'ACTIVE', 'RESOLVED', 'REFUNDED', name='bountystatus'), nullable=False, default='NONE'),
        sa.Column('accepted_post_id', sa.String(36), nullable=True),
        sa.Column('status', sa.Enum('NORMAL', 'BLOCKED', 'PENDING', name='topicstatus'), nullable=False, default='NORMAL'),
        sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),
        sa.Column('view_count', sa.Integer, nullable=False, default=0),
        sa.Column('post_count', sa.Integer, nullable=False, default=0),
        sa.Column('heat_score', sa.Float, nullable=False, default=0.0),
        sa.Column('anonymized_user_hash', sa.String(64), index=True, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_topics_heat_score'), 'topics', ['heat_score'])

    # Create posts table
    op.create_table('posts',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('topic_id', sa.String(36), index=True, nullable=False),
        sa.Column('author_id', sa.String(36), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('parent_id', sa.String(36), nullable=True),
        sa.Column('is_accepted', sa.Boolean, nullable=False, default=False),
        sa.Column('like_count', sa.Integer, nullable=False, default=0),
        sa.Column('anonymized_user_hash', sa.String(64), index=True, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'])
    )

    # Create point_ledger table
    op.create_table('point_ledger',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('transaction_uuid', sa.String(36), index=True, nullable=False),
        sa.Column('user_id', sa.String(36), index=True, nullable=False),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('point_type', sa.Enum('GOLD_BEAN', 'BONUS_BEAN', name='pointtype'), nullable=False),
        sa.Column('dist_ratio', sa.Float, nullable=True),
        sa.Column('order_type', sa.Enum(
            'DOWNLOAD', 'DOWNLOAD_REVENUE', 'DESTRUCTION', 'RECHARGE', 'SYSTEM_GIFT',
            'SHARE_REWARD', 'EARLYBIRD_REWARD', 'SIGN_IN', 'INVITE_REWARD',
            'CONTENT_TOPIC', 'CONTENT_POST', 'CATEGORY_FIRST_POST_REWARD', 'CONTENT_ADOPTED',
            'BOUNTY_LOCK', 'BOUNTY_RELEASE', 'BOUNTY_REFUND', 'FEEDBACK_AWARD',
            name='ordertype'
        ), index=True, nullable=False),
        sa.Column('balance_after', sa.Integer, nullable=False),
        sa.Column('related_id', sa.String(36), index=True, nullable=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create attempted_transaction table
    op.create_table('attempted_transaction',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), index=True, nullable=False),
        sa.Column('order_type', sa.Enum(
            'DOWNLOAD', 'DOWNLOAD_REVENUE', 'DESTRUCTION', 'RECHARGE', 'SYSTEM_GIFT',
            'SHARE_REWARD', 'EARLYBIRD_REWARD', 'SIGN_IN', 'INVITE_REWARD',
            'CONTENT_TOPIC', 'CONTENT_POST', 'CATEGORY_FIRST_POST_REWARD', 'CONTENT_ADOPTED',
            'BOUNTY_LOCK', 'BOUNTY_RELEASE', 'BOUNTY_REFUND', 'FEEDBACK_AWARD',
            name='ordertype'
        ), nullable=False),
        sa.Column('amount', sa.Integer, nullable=False),
        sa.Column('reason', sa.String(500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create asset_packages table
    op.create_table('asset_packages',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('price_beans', sa.Integer, nullable=False),
        sa.Column('quota_mb', sa.Integer, nullable=False),
        sa.Column('discount_rate', sa.Float, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_purchased_assets table
    op.create_table('user_purchased_assets',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), index=True, nullable=False),
        sa.Column('package_id', sa.String(36), nullable=False),
        sa.Column('remaining_mb', sa.Integer, nullable=False),
        sa.Column('used_mb', sa.Integer, nullable=False, default=0),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('receiver_id', sa.String(36), index=True, nullable=False),
        sa.Column('sender_id', sa.String(36), nullable=True),
        sa.Column('type', sa.Enum('SYSTEM', 'INTERACTION', 'AUDIT', 'REWARD', 'BROADCAST', name='notificationtype'), index=True, nullable=False),
        sa.Column('priority', sa.Enum('NORMAL', 'HIGH', name='notificationpriority'), nullable=False, default='NORMAL'),
        sa.Column('is_broadcast_exemption', sa.Boolean, nullable=False, default=False),
        sa.Column('title', sa.String(100), nullable=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('link_url', sa.String(500), nullable=True),
        sa.Column('is_read', sa.Boolean, nullable=False, default=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True, nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('notifications')
    op.drop_table('user_purchased_assets')
    op.drop_table('asset_packages')
    op.drop_table('attempted_transaction')
    op.drop_table('point_ledger')
    op.drop_table('posts')
    op.drop_table('topics')
    op.drop_table('resource_previews')
    op.drop_table('resources')
    op.drop_table('file_usage')
    op.drop_table('file_meta')
    op.drop_table('ai_messages')
    op.drop_table('ai_sessions')
    
    # Drop ENUM types
    sa.Enum(name='notificationpriority').drop(op.get_bind())
    sa.Enum(name='notificationtype').drop(op.get_bind())
    sa.Enum(name='ordertype').drop(op.get_bind())
    sa.Enum(name='pointtype').drop(op.get_bind())
    sa.Enum(name='topicstatus').drop(op.get_bind())
    sa.Enum(name='bountystatus').drop(op.get_bind())
    sa.Enum(name='resourcestatus').drop(op.get_bind())
    sa.Enum(name='targettype').drop(op.get_bind())
    sa.Enum(name='lifecyclestatus').drop(op.get_bind())
    sa.Enum(name='filestatus').drop(op.get_bind())

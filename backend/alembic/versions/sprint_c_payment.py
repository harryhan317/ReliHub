"""add payment tables

Revision ID: sprint_c_payment
Revises: sprint_c_llm_provider
Create Date: 2026-04-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'sprint_c_payment'
down_revision = 'sprint_c_llm_provider'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    payment_status = sa.Enum('pending', 'success', 'failed', 'refunded', 'cancelled', name='paymentstatus')
    payment_method = sa.Enum('wechat', 'alipay', 'bank_transfer', name='paymentmethod')
    
    # Create payment_orders table
    op.create_table('payment_orders',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('order_no', sa.String(64), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=True),
        sa.Column('payment_method', payment_method, nullable=True),
        sa.Column('payment_status', payment_status, nullable=True),
        sa.Column('transaction_id', sa.String(64), nullable=True),
        sa.Column('prepay_id', sa.String(128), nullable=True),
        sa.Column('subject', sa.String(255), nullable=False),
        sa.Column('body', sa.String(1000), nullable=True),
        sa.Column('callback_url', sa.String(500), nullable=True),
        sa.Column('notify_url', sa.String(500), nullable=True),
        sa.Column('metadata', sa.String(2000), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    
    # Create indexes
    op.create_index('idx_payment_orders_order_no', 'payment_orders', ['order_no'], unique=True)
    op.create_index('idx_payment_orders_user_id', 'payment_orders', ['user_id'])
    op.create_index('idx_payment_orders_user_status', 'payment_orders', ['user_id', 'payment_status'])
    op.create_index('idx_payment_orders_created', 'payment_orders', ['created_at'])
    
    # Create user_balances table
    op.create_table('user_balances',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('balance', sa.Float(), nullable=False),
        sa.Column('frozen_balance', sa.Float(), nullable=False),
        sa.Column('total_recharged', sa.Float(), nullable=False),
        sa.Column('total_consumed', sa.Float(), nullable=False),
        sa.Column('total_refunded', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    
    # Create indexes
    op.create_index('idx_user_balances_user_id', 'user_balances', ['user_id'], unique=True)
    op.create_index('idx_user_balances_balance', 'user_balances', ['balance'])
    
    # Create balance_transactions table
    op.create_table('balance_transactions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('balance_after', sa.Float(), nullable=False),
        sa.Column('payment_order_id', sa.String(36), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('remark', sa.String(1000), nullable=True),
        sa.Column('metadata', sa.String(2000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['payment_order_id'], ['payment_orders.id'], )
    )
    
    # Create indexes
    op.create_index('idx_balance_transactions_user_id', 'balance_transactions', ['user_id'])
    op.create_index('idx_balance_transactions_user_type', 'balance_transactions', ['user_id', 'transaction_type'])
    op.create_index('idx_balance_transactions_order_id', 'balance_transactions', ['payment_order_id'])
    op.create_index('idx_balance_transactions_created', 'balance_transactions', ['created_at'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('balance_transactions')
    op.drop_table('user_balances')
    op.drop_table('payment_orders')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS paymentstatus')
    op.execute('DROP TYPE IF EXISTS paymentmethod')

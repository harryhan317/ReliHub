"""add llm provider and update ai session/message

Revision ID: sprint_c_llm_provider
Revises: 43adde7206df
Create Date: 2026-04-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'sprint_c_llm_provider'
down_revision = '43adde7206df'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create llm_providers table
    op.create_table('llm_providers',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('api_base_url', sa.String(255), nullable=False),
        sa.Column('api_key_env', sa.String(100), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('rate_limit_per_minute', sa.Integer(), nullable=True, default=60),
        sa.Column('cost_per_1k_tokens', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create indexes for llm_providers
    op.create_index('idx_llm_providers_enabled', 'llm_providers', ['enabled'])
    op.create_index('idx_llm_providers_name', 'llm_providers', ['name'])
    
    # Add provider_id to ai_sessions
    op.add_column('ai_sessions', sa.Column('provider_id', sa.String(36), nullable=True))
    
    # Add total_cost to ai_sessions
    op.add_column('ai_sessions', sa.Column('total_cost', sa.Float(), nullable=True, default=0.0))
    
    # Add cost to ai_messages
    op.add_column('ai_messages', sa.Column('cost', sa.Float(), nullable=True, default=0.0))
    
    # Create foreign key for provider_id
    op.create_foreign_key(
        'fk_ai_sessions_provider',
        'ai_sessions',
        'llm_providers',
        ['provider_id'],
        ['id']
    )


def downgrade() -> None:
    # Drop foreign key
    op.drop_constraint('fk_ai_sessions_provider', 'ai_sessions', type_='foreignkey')
    
    # Drop columns
    op.drop_column('ai_messages', 'cost')
    op.drop_column('ai_sessions', 'total_cost')
    op.drop_column('ai_sessions', 'provider_id')
    
    # Drop indexes
    op.drop_index('idx_llm_providers_name', table_name='llm_providers')
    op.drop_index('idx_llm_providers_enabled', table_name='llm_providers')
    
    # Drop table
    op.drop_table('llm_providers')

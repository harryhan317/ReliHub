"""add search optimization indexes

Revision ID: sprint_e_search_indexes
Revises: 43adde7206df
Create Date: 2026-04-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'sprint_e_search_indexes'
down_revision = '43adde7206df'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add indexes to optimize search performance"""
    
    # Check if using PostgreSQL
    from alembic import context
    dialect_name = context.get_context().dialect.name
    
    # Resource indexes
    print("Creating resource indexes...")
    
    # Index on title for faster title searches
    op.create_index(
        'idx_resources_title',
        'resources',
        ['title'],
        unique=False
    )
    print("Created idx_resources_title")
    
    # Index on description for faster content searches
    if dialect_name == 'postgresql':
        op.create_index(
            'idx_resources_description',
            'resources',
            ['description'],
            unique=False,
            postgresql_using='gin',
            postgresql_ops={'description': 'gin_trgm_ops'}
        )
        print("Created idx_resources_description (GIN trigram)")
    else:
        op.create_index(
            'idx_resources_description',
            'resources',
            ['description'],
            unique=False
        )
        print("Created idx_resources_description")
    
    # Composite index for filtered and sorted queries
    op.create_index(
        'idx_resources_category_status_created',
        'resources',
        ['category_id', 'status', 'created_at'],
        unique=False
    )
    print("Created idx_resources_category_status_created")
    
    # Index on tags for tag-based searches
    if dialect_name == 'postgresql':
        op.create_index(
            'idx_resources_tags',
            'resources',
            ['tags'],
            unique=False,
            postgresql_using='gin',
            postgresql_ops={'tags': 'gin_trgm_ops'}
        )
        print("Created idx_resources_tags (GIN trigram)")
    else:
        op.create_index(
            'idx_resources_tags',
            'resources',
            ['tags'],
            unique=False
        )
        print("Created idx_resources_tags")
    
    # Full-text search index on title and description (PostgreSQL only)
    if dialect_name == 'postgresql':
        op.execute(text("""
            CREATE INDEX idx_resources_fts ON resources 
            USING gin(to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(description, '')))
        """))
        print("Created idx_resources_fts (full-text search)")
    
    # Topic indexes
    print("Creating topic indexes...")
    
    # Index on title for faster title searches
    op.create_index(
        'idx_topics_title',
        'topics',
        ['title'],
        unique=False
    )
    print("Created idx_topics_title")
    
    # Index on content for faster content searches
    if dialect_name == 'postgresql':
        op.create_index(
            'idx_topics_content',
            'topics',
            ['content'],
            unique=False,
            postgresql_using='gin',
            postgresql_ops={'content': 'gin_trgm_ops'}
        )
        print("Created idx_topics_content (GIN trigram)")
    else:
        op.create_index(
            'idx_topics_content',
            'topics',
            ['content'],
            unique=False
        )
        print("Created idx_topics_content")
    
    # Composite index for hot topic queries
    op.create_index(
        'idx_topics_category_heat',
        'topics',
        ['category_id', 'heat_score'],
        unique=False
    )
    print("Created idx_topics_category_heat")
    
    # Full-text search index on title and content (PostgreSQL only)
    if dialect_name == 'postgresql':
        op.execute(text("""
            CREATE INDEX idx_topics_fts ON topics 
            USING gin(to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(content, '')))
        """))
        print("Created idx_topics_fts (full-text search)")
    
    # AI Session indexes
    print("Creating AI session indexes...")
    
    # Index on title for faster searches
    if dialect_name == 'postgresql':
        op.create_index(
            'idx_ai_sessions_title',
            'ai_sessions',
            ['title'],
            unique=False,
            postgresql_using='gin',
            postgresql_ops={'title': 'gin_trgm_ops'}
        )
        print("Created idx_ai_sessions_title (GIN trigram)")
    else:
        op.create_index(
            'idx_ai_sessions_title',
            'ai_sessions',
            ['title'],
            unique=False
        )
        print("Created idx_ai_sessions_title")
    
    # Composite index for user's sessions sorted by date
    op.create_index(
        'idx_ai_sessions_user_created',
        'ai_sessions',
        ['user_id', 'created_at'],
        unique=False
    )
    print("Created idx_ai_sessions_user_created")
    
    # User indexes for search
    print("Creating user indexes...")
    
    # Index on nickname for user searches
    if dialect_name == 'postgresql':
        op.create_index(
            'idx_users_nickname',
            'users',
            ['nickname'],
            unique=False,
            postgresql_using='gin',
            postgresql_ops={'nickname': 'gin_trgm_ops'}
        )
        print("Created idx_users_nickname (GIN trigram)")
    else:
        op.create_index(
            'idx_users_nickname',
            'users',
            ['nickname'],
            unique=False
        )
        print("Created idx_users_nickname")
    
    print("All search optimization indexes created successfully!")


def downgrade() -> None:
    """Remove search optimization indexes"""
    
    print("Dropping search optimization indexes...")
    
    # Drop user indexes
    op.drop_index('idx_users_nickname', table_name='users')
    
    # Drop AI session indexes
    op.drop_index('idx_ai_sessions_user_created', table_name='ai_sessions')
    op.drop_index('idx_ai_sessions_title', table_name='ai_sessions')
    
    # Drop topic indexes
    op.drop_index('idx_topics_category_heat', table_name='topics')
    op.drop_index('idx_topics_content', table_name='topics')
    op.drop_index('idx_topics_title', table_name='topics')
    op.execute(text("DROP INDEX IF EXISTS idx_topics_fts"))
    
    # Drop resource indexes
    op.drop_index('idx_resources_category_status_created', table_name='resources')
    op.drop_index('idx_resources_tags', table_name='resources')
    op.drop_index('idx_resources_description', table_name='resources')
    op.drop_index('idx_resources_title', table_name='resources')
    op.execute(text("DROP INDEX IF EXISTS idx_resources_fts"))
    
    print("All search optimization indexes dropped!")

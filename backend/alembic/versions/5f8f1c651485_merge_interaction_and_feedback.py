"""merge_interaction_and_feedback

Revision ID: 5f8f1c651485
Revises: a1b2c3d4e5f6, a2b3c4d5e6f7
Create Date: 2026-04-21 20:41:19.967673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f8f1c651485'
down_revision: Union[str, None] = ('a1b2c3d4e5f6', 'a2b3c4d5e6f7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

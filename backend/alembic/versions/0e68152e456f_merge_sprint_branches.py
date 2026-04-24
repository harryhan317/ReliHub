"""merge sprint branches

Revision ID: 0e68152e456f
Revises: sprint_c_payment, sprint_e_search_indexes
Create Date: 2026-04-12 10:25:46.525729

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e68152e456f'
down_revision: Union[str, None] = ('sprint_c_payment', 'sprint_e_search_indexes')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

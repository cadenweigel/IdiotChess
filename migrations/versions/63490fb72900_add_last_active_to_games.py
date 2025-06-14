"""add last_active to games

Revision ID: 63490fb72900
Revises: 40a1d3b66ea9
Create Date: 2025-06-03 01:28:59.331515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63490fb72900'
down_revision: Union[str, None] = '40a1d3b66ea9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('last_active', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('games', 'last_active')
    # ### end Alembic commands ###

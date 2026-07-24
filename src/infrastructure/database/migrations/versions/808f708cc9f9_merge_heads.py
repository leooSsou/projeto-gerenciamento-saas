"""merge heads

Revision ID: 808f708cc9f9
Revises: 16568d6a3cca, 621df39547b1
Create Date: 2026-07-24 13:35:04.517887

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '808f708cc9f9'
down_revision: Union[str, Sequence[str], None] = ('16568d6a3cca', '621df39547b1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

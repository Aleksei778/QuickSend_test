"""add picture

Revision ID: 99561223b455
Revises: 2493e0cc7b55
Create Date: 2025-01-20 00:03:42.617794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99561223b455'
down_revision: Union[str, None] = '2493e0cc7b55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

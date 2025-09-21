"""m

Revision ID: 66019db7beb0
Revises: 99561223b455
Create Date: 2025-01-20 00:07:38.751427

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "66019db7beb0"
down_revision: Union[str, None] = "99561223b455"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

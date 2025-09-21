"""minus hashed_password from UserOrm

Revision ID: 2b0322834ef5
Revises: 9042f0f114e3
Create Date: 2024-09-21 23:39:41.402473

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2b0322834ef5"
down_revision: Union[str, None] = "9042f0f114e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удаление столбца hashed_password
    op.drop_column("users", "hashed_password")


def downgrade() -> None:
    # Откат: восстановление столбца hashed_password
    op.add_column("users", sa.Column("hashed_password", sa.String(), nullable=True))

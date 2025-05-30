"""Добавлено поле picture в модель UserOrm

Revision ID: c1b45243f353
Revises: 66019db7beb0
Create Date: 2025-01-20 00:08:55.488858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1b45243f353'
down_revision: Union[str, None] = '66019db7beb0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('picture', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'picture')
    # ### end Alembic commands ###

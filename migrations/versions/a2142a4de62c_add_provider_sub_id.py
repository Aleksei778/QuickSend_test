"""add provider_sub_id

Revision ID: a2142a4de62c
Revises: ab97d874ce16
Create Date: 2025-02-14 21:49:17.896643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2142a4de62c'
down_revision: Union[str, None] = 'ab97d874ce16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscriptions', sa.Column('provider', sa.String(), nullable=True))
    op.add_column('subscriptions', sa.Column('provider_sub_id', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'subscriptions', ['provider_sub_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'subscriptions', type_='unique')
    op.drop_column('subscriptions', 'provider_sub_id')
    op.drop_column('subscriptions', 'provider')
    # ### end Alembic commands ###

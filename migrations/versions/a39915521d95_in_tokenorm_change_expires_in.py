"""in TokenOrm change expires in

Revision ID: a39915521d95
Revises: ec7a80d3e01f
Create Date: 2024-09-22 13:53:17.287521

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a39915521d95'
down_revision: Union[str, None] = 'ec7a80d3e01f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tokens', 'expires_in',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.Integer(),
               existing_nullable=False,
               postgresql_using='extract(epoch from expires_in)::integer')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tokens', 'expires_in',
               existing_type=sa.Integer(),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)
    # ### end Alembic commands ###

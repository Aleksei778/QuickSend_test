"""changes in subscriptions and payments

Revision ID: 9adf7c102a9f
Revises: ed68be25af0d
Create Date: 2024-10-07 23:53:42.667707

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9adf7c102a9f'
down_revision: Union[str, None] = 'ed68be25af0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payments', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('payments', sa.Column('currency', sa.String(), nullable=True))
    op.add_column('payments', sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('payments', sa.Column('status', sa.String(), nullable=True))
    op.add_column('payments', sa.Column('payment_method', sa.String(), nullable=True))
    op.add_column('payments', sa.Column('transaction_id', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'payments', ['transaction_id'])
    op.drop_column('payments', 'paydatetime')
    op.add_column('subscriptions', sa.Column('plan', sa.String(), nullable=True))
    op.add_column('subscriptions', sa.Column('status', sa.String(), nullable=True))
    op.add_column('subscriptions', sa.Column('is_trial', sa.Boolean(), nullable=True))
    op.drop_column('subscriptions', 'type')
    op.drop_column('subscriptions', 'price')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscriptions', sa.Column('price', sa.NUMERIC(), autoincrement=False, nullable=False))
    op.add_column('subscriptions', sa.Column('type', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('subscriptions', 'is_trial')
    op.drop_column('subscriptions', 'status')
    op.drop_column('subscriptions', 'plan')
    op.add_column('payments', sa.Column('paydatetime', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'payments', type_='unique')
    op.drop_column('payments', 'transaction_id')
    op.drop_column('payments', 'payment_method')
    op.drop_column('payments', 'status')
    op.drop_column('payments', 'amount')
    op.drop_column('payments', 'currency')
    op.drop_column('payments', 'created_at')
    # ### end Alembic commands ###

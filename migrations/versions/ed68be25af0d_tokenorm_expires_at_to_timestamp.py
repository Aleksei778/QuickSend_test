"""TokenOrm expires_at to TIMESTAMP

Revision ID: ed68be25af0d
Revises: a39915521d95
Create Date: 2024-09-22 14:07:25.182872

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ed68be25af0d"
down_revision: Union[str, None] = "a39915521d95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Изменяем тип столбца expires_at на TIMESTAMP
    op.alter_column(
        "tokens",  # имя таблицы
        "expires_at",  # имя столбца
        type_=sa.TIMESTAMP(),  # новый тип
        postgresql_using="expires_at::timestamp",  # явное преобразование, если нужно
    )


def downgrade() -> None:
    # Возвращаем тип столбца обратно (например, на DATE, если это был исходный тип)
    op.alter_column(
        "tokens",
        "expires_at",
        type_=sa.TIMESTAMP(),  # измените на нужный тип
        postgresql_using="expires_at::timestamp",  # явное преобразование, если нужно
    )

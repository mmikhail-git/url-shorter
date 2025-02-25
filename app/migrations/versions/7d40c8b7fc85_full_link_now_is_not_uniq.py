"""full_link now is not uniq

Revision ID: 7d40c8b7fc85
Revises: 9179ec0e2037
Create Date: 2025-02-06 15:03:09.499427

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d40c8b7fc85'
down_revision: Union[str, None] = '9179ec0e2037'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('links_full_link_key', 'links', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('links_full_link_key', 'links', ['full_link'])
    # ### end Alembic commands ###

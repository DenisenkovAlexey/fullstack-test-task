"""add_content_hash

Revision ID: 2b3c4d5e6f7a
Revises: 1a2b3c4d5e6f
Create Date: 2026-07-08 14:41:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b3c4d5e6f7a'
down_revision: Union[str, Sequence[str], None] = '1a2b3c4d5e6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('files', sa.Column('content_hash', sa.String(length=64), nullable=True))
    op.create_unique_constraint(None, 'files', ['content_hash'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'files', type_='unique')
    op.drop_column('files', 'content_hash')

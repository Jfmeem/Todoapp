"""phn column adding for users table

Revision ID: 90afdad96ad3
Revises: 
Create Date: 2026-11-25 22:07:57.019821

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90afdad96ad3'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phn', sa.String(20), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
"""Add permissions column to roles table if missing

Revision ID: a83659e3997a
Revises: 6c287209dc634736
Create Date: 2025-11-26 15:11:15.882660

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a83659e3997a'
down_revision: Union[str, Sequence[str], None] = '6c287209dc634736'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add the missing permissions column to roles table
    op.add_column('roles', sa.Column('permissions', sa.String(length=1000), nullable=True, default="[]"))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the permissions column from roles table
    op.drop_column('roles', 'permissions')

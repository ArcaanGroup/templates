"""Add missing roles tables

Revision ID: 6c287209dc634736
Revises: c5b9c06166ca
Create Date: 2025-11-26 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c287209dc634736'
down_revision: Union[str, Sequence[str], None] = 'c5b9c06166ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create roles table
    op.create_table('roles',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('title', sa.String(50), nullable=False),
        sa.Column('description', sa.String(250), nullable=True),
        sa.Column('permissions', sa.String(1000), nullable=True, default="[]"),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_unique_constraint('uq_roles_title', 'roles', ['title'])

    # Create user_roles association table
    op.create_table('user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.String(36), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop user_roles association table first
    op.drop_table('user_roles')

    # Drop roles table
    op.drop_constraint('uq_roles_title', 'roles', type_='unique')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')

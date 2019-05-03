"""empty message

Revision ID: 09e2a2a1c419
Revises: 6fabf5d1d308
Create Date: 2019-05-03 15:19:34.701144

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09e2a2a1c419'
down_revision = '6fabf5d1d308'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('posts', 'body', existing_type=sa.String(5000), type_=sa.TEXT())


def downgrade():
    op.alter_column('posts', 'body', type_=sa.String(5000), existing_type=sa.TEXT())

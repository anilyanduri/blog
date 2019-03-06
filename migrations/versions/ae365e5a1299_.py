"""empty message

Revision ID: ae365e5a1299
Revises: f563230b7701
Create Date: 2019-02-21 12:24:33.544443

"""
from alembic import op
from blog.constants import KEY_WORDS


# revision identifiers, used by Alembic.
revision = 'ae365e5a1299'
down_revision = 'f563230b7701'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    for key_pair in KEY_WORDS:
        conn.execute("insert into tags (tag_name, category, created_at, updated_at) values('{}', 'tag', now(), now())".
                     format(key_pair[0]))


def downgrade():
    pass

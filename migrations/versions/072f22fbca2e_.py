"""empty message

Revision ID: 072f22fbca2e
Revises: 9475cc19950a
Create Date: 2019-02-28 14:09:46.104792

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '072f22fbca2e'
down_revision = '9475cc19950a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('photographs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('photograph_url', sa.String(length=1000), nullable=True),
    sa.Column('title', sa.String(length=250), nullable=True),
    sa.Column('href', sa.String(length=250), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('photo_tags',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('photograph_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['photograph_id'], ['photographs.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], )
    )
    op.drop_table('comments')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('comment', mysql.VARCHAR(length=250), nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('post_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['post_id'], [u'posts.id'], name=u'comments_ibfk_1'),
    sa.ForeignKeyConstraint(['user_id'], [u'users.id'], name=u'comments_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.drop_table('photo_tags')
    op.drop_table('photographs')
    # ### end Alembic commands ###

"""empty message

Revision ID: 6c942afc17fd
Revises: f61d3d451202
Create Date: 2020-07-09 14:39:16.435428

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c942afc17fd'
down_revision = 'f61d3d451202'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.name'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.name'], ),
    sa.PrimaryKeyConstraint('id', 'artist_id', 'venue_id')
    )
    op.drop_table('show_list')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('show_list',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], name='show_list_artist_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], name='show_list_venue_id_fkey'),
    sa.PrimaryKeyConstraint('id', 'artist_id', 'venue_id', name='show_list_pkey')
    )
    op.drop_table('show')
    # ### end Alembic commands ###

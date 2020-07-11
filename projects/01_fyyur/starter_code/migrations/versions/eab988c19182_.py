"""empty message

Revision ID: eab988c19182
Revises: d5de5f8202d2
Create Date: 2020-07-10 19:48:56.567092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eab988c19182'
down_revision = 'd5de5f8202d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('artist_name', sa.String(), nullable=True))
    op.add_column('show', sa.Column('venue_name', sa.String(), nullable=True))
    op.create_foreign_key(None, 'show', 'venue', ['venue_name'], ['name'])
    op.create_foreign_key(None, 'show', 'artist', ['artist_name'], ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'show', type_='foreignkey')
    op.drop_constraint(None, 'show', type_='foreignkey')
    op.drop_column('show', 'venue_name')
    op.drop_column('show', 'artist_name')
    # ### end Alembic commands ###
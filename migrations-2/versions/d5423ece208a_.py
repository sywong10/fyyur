"""empty message

Revision ID: d5423ece208a
Revises: 
Create Date: 2022-01-04 21:31:55.612091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5423ece208a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('website', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    # ### end Alembic commands ###

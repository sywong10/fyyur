"""empty message

Revision ID: 00bd1d9db943
Revises: b6a2fd5069db
Create Date: 2022-01-05 06:59:26.780601

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00bd1d9db943'
down_revision = 'b6a2fd5069db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('facebook_link', sa.String(length=120), nullable=True))
    op.add_column('Artist', sa.Column('website', sa.String(length=50), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'facebook_link')
    # ### end Alembic commands ###
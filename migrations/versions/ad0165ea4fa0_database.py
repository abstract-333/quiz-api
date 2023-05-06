"""Database

Revision ID: ad0165ea4fa0
Revises: b167486d8665
Create Date: 2023-04-30 03:28:27.123385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad0165ea4fa0'
down_revision = 'b167486d8665'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('quiz', sa.Column('resolve_time', sa.Integer(), nullable=False))
    op.add_column('quiz', sa.Column('question', sa.String(length=200), nullable=False))
    op.add_column('quiz', sa.Column('choices', sa.JSON(), nullable=False))
    op.add_column('quiz', sa.Column('answer', sa.Integer(), nullable=False))
    op.add_column('quiz', sa.Column('added_by', sa.String(length=25), nullable=False))
    op.add_column('quiz', sa.Column('added_at', sa.TIMESTAMP(), nullable=True))
    op.add_column('quiz', sa.Column('type', sa.String(length=25), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('quiz', 'type')
    op.drop_column('quiz', 'added_at')
    op.drop_column('quiz', 'added_by')
    op.drop_column('quiz', 'answer')
    op.drop_column('quiz', 'choices')
    op.drop_column('quiz', 'question')
    op.drop_column('quiz', 'resolve_time')
    # ### end Alembic commands ###

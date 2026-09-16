"""Add equipment type rating

Revision ID: c1a2b3c4d5e6
Revises: b000f2425625
Create Date: 2026-09-16 21:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c1a2b3c4d5e6"
down_revision = "b000f2425625"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("equipment_type", sa.Column("rating", sa.String(length=50), nullable=True))


def downgrade():
    op.drop_column("equipment_type", "rating")

"""fix missing server default on events created_at

Revision ID: 9153016d9fd7
Revises: 7f7a8a510c94
Create Date: 2026-06-19 13:21:44.188100

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9153016d9fd7"
down_revision = "7f7a8a510c94"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE events ALTER COLUMN created_at SET DEFAULT now()")


def downgrade():
    op.execute("ALTER TABLE events ALTER COLUMN created_at DROP DEFAULT")

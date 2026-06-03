"""fill categories

Revision ID: a041cb02067e
Revises: 99bfa96e473a
Create Date: 2026-06-03 08:56:23.835316

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a041cb02067e"
down_revision = "99bfa96e473a"
branch_labels = None
depends_on = None


def upgrade():
    op.bulk_insert(
        sa.table(
            "event_categories",
            sa.column("name", sa.String),
        ),
        [
            {"name": "Music"},
            {"name": "Sports"},
            {"name": "Technology"},
            {"name": "Arts & Theater"},
            {"name": "Food & Drink"},
            {"name": "Business & Networking"},
            {"name": "Health & Wellness"},
            {"name": "Education"},
            {"name": "Comedy"},
            {"name": "Film & Media"},
            {"name": "Gaming"},
            {"name": "Travel & Outdoor"},
            {"name": "Fashion"},
            {"name": "Charity & Causes"},
            {"name": "Family & Kids"},
        ],
    )


def downgrade():
    op.execute("DELETE FROM event_categories")

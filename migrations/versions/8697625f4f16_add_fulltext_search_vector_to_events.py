"""add fulltext search vector to events

Revision ID: 8697625f4f16
Revises: 0976da41f096
Create Date: 2026-06-19 09:51:58.806868

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8697625f4f16"
down_revision = "0976da41f096"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE events ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
            setweight(to_tsvector('english', coalesce(description, '')), 'B') ||
            setweight(to_tsvector('english', coalesce(location, '')), 'C')
        ) STORED
    """)

    op.execute("""
        CREATE INDEX events_search_vector_idx ON events USING GIN (search_vector)
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS events_search_vector_idx")
    op.execute("ALTER TABLE events DROP COLUMN IF EXISTS search_vector")

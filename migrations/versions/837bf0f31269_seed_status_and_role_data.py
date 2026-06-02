"""seed status and role data

Revision ID: 837bf0f31269
Revises: 19aa16dfc5c5
Create Date: 2026-06-02 08:53:38.623982

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "837bf0f31269"
down_revision = "19aa16dfc5c5"
branch_labels = None
depends_on = None


def upgrade():

    op.bulk_insert(
        sa.table(
            "user_roles",
            sa.column("name", sa.String),
        ),
        [
            {"name": "attendee"},
            {"name": "organizer"},
            {"name": "admin"},
        ],
    )

    op.bulk_insert(
        sa.table(
            "user_statuses",
            sa.column("name", sa.String),
            sa.column("description", sa.String),
            sa.column("is_terminal", sa.Boolean),
        ),
        [
            {"name": "active", "description": "User is active", "is_terminal": False},
            {
                "name": "suspended",
                "description": "User is suspended",
                "is_terminal": False,
            },
            {"name": "deleted", "description": "User is deleted", "is_terminal": True},
        ],
    )

    op.bulk_insert(
        sa.table(
            "event_statuses",
            sa.column("name", sa.String),
            sa.column("description", sa.String),
            sa.column("is_terminal", sa.Boolean),
        ),
        [
            {
                "name": "draft",
                "description": "not yet visible publicly",
                "is_terminal": False,
            },
            {
                "name": "published",
                "description": "live and accepting registrations",
                "is_terminal": False,
            },
            {
                "name": "cancelled",
                "description": "called off",
                "is_terminal": True,
            },
            {
                "name": "completed",
                "description": "event has passed",
                "is_terminal": True,
            },
        ],
    )

    op.bulk_insert(
        sa.table(
            "order_statuses",
            sa.column("name", sa.String),
            sa.column("description", sa.String),
            sa.column("is_terminal", sa.Boolean),
        ),
        [
            {
                "name": "pending",
                "description": "checkout started, payment not confirmed",
                "is_terminal": False,
            },
            {
                "name": "confirmed",
                "description": "payment successful",
                "is_terminal": False,
            },
            {
                "name": "cancelled",
                "description": "order cancelled",
                "is_terminal": True,
            },
            {
                "name": "refunded",
                "description": "fully refunded",
                "is_terminal": True,
            },
        ],
    )

    op.bulk_insert(
        sa.table(
            "ticket_statuses",
            sa.column("name", sa.String),
            sa.column("description", sa.String),
            sa.column("is_terminal", sa.Boolean),
        ),
        [
            {
                "name": "reserved",
                "description": "held during checkout, not yet paid",
                "is_terminal": False,
            },
            {
                "name": "confirmed",
                "description": "paid and valid",
                "is_terminal": False,
            },
            {
                "name": "cancelled",
                "description": "cancelled",
                "is_terminal": True,
            },
            {
                "name": "refunded",
                "description": "refunded",
                "is_terminal": True,
            },
            {
                "name": "used",
                "description": "checked in at the door",
                "is_terminal": True,
            },
        ],
    )

    op.bulk_insert(
        sa.table(
            "rsvp_statuses",
            sa.column("name", sa.String),
            sa.column("description", sa.String),
            sa.column("is_terminal", sa.Boolean),
        ),
        [
            {
                "name": "confirmed",
                "description": "attending",
                "is_terminal": False,
            },
            {
                "name": "cancelled",
                "description": "no longer attending",
                "is_terminal": True,
            },
        ],
    )


def downgrade():
    op.execute("DELETE FROM user_roles")
    op.execute("DELETE FROM user_statuses")
    op.execute("DELETE FROM event_statuses")
    op.execute("DELETE FROM order_statuses")
    op.execute("DELETE FROM ticket_statuses")
    op.execute("DELETE FROM rsvp_statuses")

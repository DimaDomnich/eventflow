"""rename status and role tables to dict prefix

Revision ID: 99bfa96e473a
Revises: 837bf0f31269
Create Date: 2026-06-02 09:27:47.198163

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "99bfa96e473a"
down_revision = "837bf0f31269"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("user_statuses", "dict_user_statuses")
    op.rename_table("user_roles", "dict_user_roles")
    op.rename_table("event_statuses", "dict_event_statuses")
    op.rename_table("order_statuses", "dict_order_statuses")
    op.rename_table("ticket_statuses", "dict_ticket_statuses")
    op.rename_table("rsvp_statuses", "dict_rsvp_statuses")


def downgrade():
    op.rename_table("dict_user_statuses", "user_statuses")
    op.rename_table("dict_user_roles", "user_roles")
    op.rename_table("dict_event_statuses", "event_statuses")
    op.rename_table("dict_order_statuses", "order_statuses")
    op.rename_table("dict_ticket_statuses", "ticket_statuses")
    op.rename_table("dict_rsvp_statuses", "rsvp_statuses")

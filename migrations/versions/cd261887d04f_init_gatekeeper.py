"""Init gatekeeper

Revision ID: cd261887d04f
Revises: 
Create Date: 2021-02-17 12:08:12.450227

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd261887d04f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("gk_bans", sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.String),
        sa.Column("reason", sa.String, default="No reason provided"),
        sa.Column("moderator", sa.String)
        )

    op.create_table("gk_mods",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("user_id", sa.String)
            )


def downgrade():
    op.drop_table("gk_bans")
    op.drop_table("gk_mods")

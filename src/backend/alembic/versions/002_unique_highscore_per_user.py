"""one highscore per user

Revision ID: 002
Revises: 001
Create Date: 2026-04-17
"""

from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove duplicate rows, keeping only the highest score per user
    op.execute("""
        DELETE FROM highscores
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM (
                SELECT id, user_id, score,
                       RANK() OVER (PARTITION BY user_id ORDER BY score DESC) AS rnk
                FROM highscores
            ) ranked
            WHERE rnk = 1
        )
    """)
    op.create_unique_constraint("uq_highscores_user_id", "highscores", ["user_id"])


def downgrade() -> None:
    op.drop_constraint("uq_highscores_user_id", "highscores", type_="unique")

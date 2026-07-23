import sqlalchemy as sa

from alembic import op

revision = "70e8b60f7571"
down_revision = "04e541807839"
branch_labels = None
depends_on = None


task_status = sa.Enum(
    "pending",
    "in_progress",
    "completed",
    "cancelled",
    name="taskstatus",
)


def upgrade():
    task_status.create(op.get_bind(), checkfirst=True)

    op.execute("""
        ALTER TABLE user_tasks
        ALTER COLUMN status
        TYPE taskstatus
        USING status::taskstatus
    """)


def downgrade():
    op.execute("""
        ALTER TABLE user_tasks
        ALTER COLUMN status
        TYPE VARCHAR(25)
    """)

    task_status.drop(op.get_bind(), checkfirst=True)

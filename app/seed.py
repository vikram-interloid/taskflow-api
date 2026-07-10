from datetime import datetime, timedelta, UTC

from sqlalchemy.orm import Session

from app.api.database.db_config import SessionLocal

from app.api.core.security import hash_password

from app.api.models.roles_model import Role
from app.api.models.users_model import User
from app.api.models.user_role import UserRole
from app.api.models.task_model import Task
from app.api.models.user_task import UserTask
from app.api.enums.task_status import TaskStatus


def seed_database() -> None:
    db: Session = SessionLocal()

    try:
        print("Seeding database...")

        # -----------------------------
        # Roles
        # -----------------------------

        admin_role = Role(role_name="Admin")
        manager_role = Role(role_name="Manager")
        employee_role = Role(role_name="Employee")

        db.add_all([
            admin_role,
            manager_role,
            employee_role,
        ])

        db.commit()

        # -----------------------------
        # Users
        # -----------------------------

        admin = User(
            user_name="admin",
            email="admin@example.com",
            password_hash=hash_password("Admin@123"),
        )

        manager = User(
            user_name="manager",
            email="manager@example.com",
            password_hash=hash_password("Manager@123"),
        )

        john = User(
            user_name="john",
            email="john@example.com",
            password_hash=hash_password("John@123"),
        )

        alice = User(
            user_name="alice",
            email="alice@example.com",
            password_hash=hash_password("Alice@123"),
        )

        db.add_all([
            admin,
            manager,
            john,
            alice,
        ])

        db.commit()

        print("Roles created")
        print("Users created")
        
                # -----------------------------
        # User Role Assignments
        # -----------------------------

        user_roles = [
            UserRole(
                user_id=admin.user_id,
                role_id=admin_role.role_id,
                assigned_by=admin.user_id,
            ),
            UserRole(
                user_id=manager.user_id,
                role_id=manager_role.role_id,
                assigned_by=admin.user_id,
            ),
            UserRole(
                user_id=john.user_id,
                role_id=employee_role.role_id,
                assigned_by=admin.user_id,
            ),
            UserRole(
                user_id=alice.user_id,
                role_id=employee_role.role_id,
                assigned_by=manager.user_id,
            ),
        ]

        db.add_all(user_roles)
        db.commit()

        print("User roles assigned")

        # -----------------------------
        # Tasks
        # -----------------------------

        task1 = Task(
            task_name="Setup FastAPI Project",
            task_desc="Create project structure and configure dependencies.",
            created_by=admin.user_id,
        )

        task2 = Task(
            task_name="Implement Authentication",
            task_desc="Develop JWT login and refresh token flow.",
            created_by=admin.user_id,
        )

        task3 = Task(
            task_name="Design Database",
            task_desc="Create SQLAlchemy models and Alembic migrations.",
            created_by=manager.user_id,
        )

        task4 = Task(
            task_name="Implement Redis Cache",
            task_desc="Cache GET endpoints using Redis.",
            created_by=manager.user_id,
        )

        task5 = Task(
            task_name="Write API Documentation",
            task_desc="Prepare Swagger documentation and endpoint examples.",
            created_by=admin.user_id,
        )

        db.add_all([
            task1,
            task2,
            task3,
            task4,
            task5,
        ])

        db.commit()

        print("Tasks created")
        
                # -----------------------------
        # User Task Assignments
        # -----------------------------

        now = datetime.now(UTC)

        user_tasks = [
            UserTask(
                task_id=task1.task_id,
                user_id=john.user_id,
                created_by=admin.user_id,
                due_at=now + timedelta(days=5),
                status=TaskStatus.PENDING,
            ),
            UserTask(
                task_id=task2.task_id,
                user_id=john.user_id,
                created_by=admin.user_id,
                due_at=now + timedelta(days=10),
                status=TaskStatus.IN_PROGRESS,
            ),
            UserTask(
                task_id=task3.task_id,
                user_id=alice.user_id,
                created_by=manager.user_id,
                due_at=now + timedelta(days=7),
                status=TaskStatus.COMPLETED,
                completed_at=now,
            ),
            UserTask(
                task_id=task4.task_id,
                user_id=alice.user_id,
                created_by=manager.user_id,
                due_at=now + timedelta(days=3),
                status=TaskStatus.CANCELLED,
            ),
            UserTask(
                task_id=task5.task_id,
                user_id=manager.user_id,
                created_by=admin.user_id,
                due_at=now + timedelta(days=14),
                status=TaskStatus.PENDING,
            ),
        ]

        db.add_all(user_tasks)
        db.commit()

        print("User tasks assigned")
        print("Database seeded successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error while seeding database: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
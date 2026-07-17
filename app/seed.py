from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.api.core.security import hash_password
from app.api.database.db_config import SessionLocal
from app.api.enums.task_status import TaskStatus
from app.api.models.roles_model import Role
from app.api.models.task_model import Task
from app.api.models.user_role import UserRole
from app.api.models.user_task import UserTask
from app.api.models.users_model import User


def seed_database() -> None:
    db: Session = SessionLocal()

    try:
        print("Seeding database...")

        # -----------------------------
        # Roles
        # -----------------------------

        admin_role = Role(role_name="Admin")
        manager_role = Role(role_name="Manager")
        user_role = Role(role_name="User")

        db.add_all(
            [
                admin_role,
                manager_role,
                user_role,
            ]
        )

        db.commit()

        print("Roles created")

        # -----------------------------
        # Users
        # -----------------------------

        users = {}

        user_data = [
            ("Siva", "siva@taskflow.com"),
            ("Boopathi", "boopathi@taskflow.com"),
            ("Ram", "ram@taskflow.com"),
            ("Vikram", "vikram@taskflow.com"),
            ("Naveen", "naveen@taskflow.com"),
            ("Guru", "guru@taskflow.com"),
            ("Amana", "amana@taskflow.com"),
            ("Amaldas", "amaldas@taskflow.com"),
            ("Hari", "hari@taskflow.com"),
            ("Karthik", "karthik@taskflow.com"),
            ("Ajith", "ajith@taskflow.com"),
            ("Surya", "surya@taskflow.com"),
            ("Dinesh", "dinesh@taskflow.com"),
            ("Praveen", "praveen@taskflow.com"),
            ("Arun", "arun@taskflow.com"),
            ("Bala", "bala@taskflow.com"),
            ("Vignesh", "vignesh@taskflow.com"),
            ("Ashok", "ashok@taskflow.com"),
            ("Sanjay", "sanjay@taskflow.com"),
            ("Kumar", "kumar@taskflow.com"),
        ]

        for username, email in user_data:

            user = User(
                user_name=username,
                email=email,
                password_hash=hash_password("Password@123"),
            )

            db.add(user)

            users[username] = user

        db.commit()

        print("Users created")

        # -----------------------------
        # User Role Assignments
        # -----------------------------

        role_map = {
            "Admin": admin_role,
            "Manager": manager_role,
            "User": user_role,
        }

        user_role_map = {
            "Siva": ["Admin"],
            "Vikram": ["Admin", "Manager"],
            "Boopathi": ["Manager"],
            "Ram": ["Manager"],
            "Naveen": ["User", "Manager", "Admin"],
            "Guru": ["User", "Manager", "Admin"],
            "Amana": ["User", "Manager", "Admin"],
            "Amaldas": ["User"],
            "Hari": ["User"],
            "Karthik": ["User"],
            "Ajith": ["User"],
            "Surya": ["User"],
            "Dinesh": ["User"],
            "Praveen": ["User"],
            "Arun": ["User"],
            "Bala": ["User"],
            "Vignesh": ["User"],
            "Ashok": ["User"],
            "Sanjay": ["User"],
            "Kumar": ["User"],
        }

        user_roles = []

        admin_user = users["Siva"]

        for username, roles in user_role_map.items():

            for role_name in roles:

                user_roles.append(
                    UserRole(
                        user_id=users[username].user_id,
                        role_id=role_map[role_name].role_id,
                        assigned_by=admin_user.user_id,
                    )
                )

        db.add_all(user_roles)

        db.commit()

        print("User roles assigned")

        # -----------------------------
        # Tasks
        # -----------------------------

        task_names = [
            "FastAPI Authentication",
            "JWT Login",
            "RBAC Implementation",
            "User CRUD",
            "Role CRUD",
            "Task CRUD",
            "Redis Cache",
            "Alembic Migration",
            "Docker Setup",
            "GitHub Actions",
            "Python OOP",
            "Async Programming",
            "PostgreSQL Indexing",
            "Database Optimization",
            "SQL Joins",
            "MongoDB Aggregation",
            "REST API Design",
            "Unit Testing",
            "Integration Testing",
            "Logging System",
            "AWS EC2",
            "AWS S3",
            "AWS IAM",
            "Terraform",
            "Nginx",
            "Kafka Basics",
            "RabbitMQ",
            "Celery",
            "WebSockets",
            "Background Tasks",
            "LLM Basics",
            "Prompt Engineering",
            "RAG Pipeline",
            "LangChain",
            "Qdrant",
            "FAISS",
            "Vector Search",
            "Embedding Models",
            "OpenAI API",
            "Ollama",
            "React Hooks",
            "React Query",
            "TypeScript",
            "Next.js",
            "Tailwind CSS",
            "Linux Commands",
            "Bash Scripting",
            "Firewall Rules",
            "DNS",
            "CI/CD Pipeline",
        ]

        tasks = []

        for index, task_name in enumerate(task_names):

            if index < 10:
                creator = users["Siva"]

            elif index < 25:
                creator = users["Vikram"]

            elif index < 38:
                creator = users["Boopathi"]

            else:
                creator = users["Ram"]

            task = Task(
                task_name=task_name,
                task_desc=f"Complete the {task_name} module.",
                created_by=creator.user_id,
            )

            db.add(task)

            tasks.append(task)

        db.commit()

        print("50 Tasks created")

        # -----------------------------
        # User Task Assignments
        # -----------------------------

        now = datetime.now(UTC)

        employees = [
            users["Naveen"],
            users["Guru"],
            users["Amana"],
            users["Amaldas"],
            users["Hari"],
            users["Karthik"],
            users["Ajith"],
            users["Surya"],
            users["Dinesh"],
            users["Praveen"],
            users["Arun"],
            users["Bala"],
            users["Vignesh"],
            users["Ashok"],
            users["Sanjay"],
            users["Kumar"],
        ]

        status_cycle = [
            TaskStatus.PENDING,
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
        ]

        user_tasks = []

        for index, task in enumerate(tasks):

            employee = employees[index % len(employees)]

            status = status_cycle[index % len(status_cycle)]

            creator = task.creator

            completed_at = None

            if status == TaskStatus.COMPLETED:
                completed_at = now

            user_tasks.append(
                UserTask(
                    task_id=task.task_id,
                    user_id=employee.user_id,
                    created_by=creator.user_id,
                    due_at=now + timedelta(days=index + 2),
                    status=status,
                    completed_at=completed_at,
                )
            )

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

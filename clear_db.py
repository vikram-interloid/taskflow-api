from app.api.database.db_config import SessionLocal
from app.api.models.roles_model import Role
from app.api.models.task_model import Task
from app.api.models.user_role import UserRole
from app.api.models.user_task import UserTask
from app.api.models.users_model import User

db = SessionLocal()

try:
    db.query(UserTask).delete()
    db.query(UserRole).delete()
    db.query(Task).delete()
    db.query(User).delete()
    db.query(Role).delete()

    db.commit()

    print("Database cleared successfully.")

except Exception as e:
    db.rollback()
    print(e)

finally:
    db.close()
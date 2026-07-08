from fastapi import Depends, FastAPI

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.database.db_config import get_db
from app.api.routers.user_router import router as user_router
from app.api.routers.role_router import router as role_router
from app.api.routers.task_router import router as task_router
from app.api.routers.user_role_router import router as user_role_router
from app.api.routers.user_task_router import router as user_task_router



app = FastAPI()

app.include_router(user_router)
app.include_router(role_router)
app.include_router(task_router)
app.include_router(user_role_router)
app.include_router(user_task_router)


@app.get('/')
def home():
    return {
       'message':'Welcome to TaskFlow-Api'
    }


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"message": "Database connected successfully"}
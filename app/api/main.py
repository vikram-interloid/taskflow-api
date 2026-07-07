from fastapi import Depends, FastAPI

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.database.db_config import get_db

app = FastAPI()

@app.get('/')
def home():
    return {
       'message':'Welcome to TaskFlow-Api'
    }


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"message": "Database connected successfully"}
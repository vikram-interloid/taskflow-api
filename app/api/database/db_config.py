import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_PORT = os.getenv("DATABASE_PORT")


# DATABASE_URL = ("postgresql+psycopg://postgres:postgres@localhost:5432/task_management_db")

DATABASE_URL = (f"postgresql+psycopg://"f"{DATABASE_USER}:{DATABASE_PASSWORD}"f"@{DATABASE_HOST}:{DATABASE_PORT}"f"/{DATABASE_NAME}")


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind = engine, autoflush = False, autocommit = False)

class Base(DeclarativeBase):
    pass

def get_db(Base) :
    db = SessionLocal
    try : 
        yield db
    finally : 
        db.close()
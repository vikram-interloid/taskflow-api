# TaskFlow API
A FastAPI-based Task Management REST API with JWT Authentication, Role-Based Access Control (RBAC), PostgreSQL, Redis, Docker, and Alembic.

# Setup

## Prerequisites
- Python 3.12+
- PostgreSQL (or Neon)
- Redis (or Redis cloud console)

## Installation & SetupClone 

git clone git@github.com:vikram-interloid/taskflow-api.git

cd taskflow-api

## Create a virtual environment 
python3 -m venv venv

### On Linux  
source venv/bin/activate  

### On Windows 
venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Configure Environment Variables
### Create a .env file in the root directory

- SECRET_KEY="your-secret-jwt-key"
- ALGORITHM="HS256"
- ACCESS_TOKEN_EXPIRE_MINUTES=30


# Run Database Migrations

alembic upgrade head


# Seed Database

python3 -m app.seed


# Start the Run Server
uvicorn app.api.main:app --reload

# Application:

http://127.0.0.1:8000


# Swagger UI:

http://127.0.0.1:8000/docs



# TaskFlow API

A production-ready Task Management REST API built with **FastAPI**, following the **Repository → Service → Router** architecture with **JWT Authentication**, **Role-Based Access Control (RBAC)**, **Redis Caching**, and **PostgreSQL**.

---

# Features

* JWT Authentication
* Refresh Token Authentication
* Role-Based Access Control (RBAC)
* CRUD APIs
* Repository Pattern
* Service Layer
* SQLAlchemy ORM
* Alembic Migrations
* PostgreSQL Database
* Redis Caching
* Rate Limiting
* Pagination
* Filtering
* Sorting
* Soft API Versioning (`/api/v1`)
* Pydantic Validation
* Exception Handling

---

# Tech Stack

| Technology | Version |
| ---------- | ------- |
| Python     | 3.12+   |
| FastAPI    | latest  |
| SQLAlchemy | 2.x     |
| PostgreSQL | 16+     |
| Redis      | 7+      |
| Alembic    | latest  |
| Pydantic   | 2.x     |
| Uvicorn    | latest  |

---

# Project Structure

```text
taskflow-api/
│
├── alembic/
│
├── app/
│   ├── api/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   ├── rbac.py
│   │   ├── limiter.py
│   │   └── auth_middleware.py
│   │
│   ├── database/
│   │   ├── db_config.py
│   │   └── redis.py
│   │
│   ├── enums/
│   │
│   ├── models/
│   │
│   ├── repositories/
│   │
│   ├── routers/
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │
│   └── main.py
│
├── .env
├── alembic.ini
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

# Architecture Flow

```
Client
   │
   ▼
FastAPI Router
   │
   ▼
Service Layer
   │
   ▼
Repository Layer
   │
   ▼
SQLAlchemy ORM
   │
   ▼
PostgreSQL
```

For cached requests:

```
Client
   │
   ▼
Router
   │
   ▼
Service
   │
   ├────────► Redis Cache
   │             │
   │             ▼
   │        Cache Hit
   │
   ▼
Repository
   │
PostgreSQL
```

---

# Database Tables

* Users
* Roles
* UserRoles
* Tasks
* UserTasks
* RefreshTokens

---

---

# Setup

## 1 Clone

```bash
git clone <repository_url>

cd taskflow-api
```

---

## 2 Create Virtual Environment

Linux

```bash
python3 -m venv taskvenv

source taskvenv/bin/activate
```

Windows

```bash
python -m venv taskvenv

taskvenv\Scripts\activate
```

---

## 3 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4 Create `.env`

Example

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/taskflow

SECRET_KEY=your-secret-key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

REFRESH_TOKEN_EXPIRE_DAYS=7

REDIS_HOST=localhost

REDIS_PORT=6379

REDIS_DB=0
```

---

## 5 Run PostgreSQL

Example with Docker

```bash
docker run -d \
--name postgres \
-p 5432:5432 \
-e POSTGRES_PASSWORD=password \
postgres:16
```

---

## 6 Run Redis

```bash
docker run -d \
--name redis \
-p 6379:6379 \
redis:7
```

---

## 7 Run Migrations

```bash
alembic upgrade head
```

---

## 8 Start Server

```bash
uvicorn app.main:app --reload
```

---

# API Documentation

Swagger

```
http://localhost:8000/docs
```

---

# Development Commands

Run Server

```bash
uvicorn app.main:app --reload
```


# Future Improvements

* Email Verification
* Password Reset
* Audit Logs
* Background Tasks
* Docker Compose
* CI/CD Pipeline
* Unit & Integration Tests
* OpenTelemetry
* Prometheus & Grafana Monitoring

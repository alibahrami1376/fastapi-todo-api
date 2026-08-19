<!-- Language switcher -->
<p align="right">
  <a href="#persian-version">🇮🇷 فارسی</a> &nbsp;|&nbsp;
  <a href="#english-version">🇬🇧 English</a>
</p>

---

<a name="english-version"></a>

# FastAPI Todo API 🇬🇧

A production-ready REST API for managing personal todo tasks, built with **FastAPI**, **SQLAlchemy**, **PostgreSQL**, and **JWT authentication** following a clean layered architecture.

- [Overview](#overview-en)
- [Features](#features-en)
- [Requirements](#requirements-en)
- [Configuration](#configuration-en)
- [Installation](#installation-en)
- [Usage](#usage-en)
  - [Seed fake data](#seed-en)
  - [Documentation](#documentation-en)
  - [Testing](#testing-en)
  - [Lint and Reformat](#lint-en)
- [Project Structure](#structure-en)
- [Architecture](#architecture-en)
- [Known Issues](#known-issues-en)
- [License](#license-en)

---

<a name="overview-en"></a>
## Overview

FastAPI Todo API is a backend service that lets authenticated users create, read, update, delete and search their personal todo tasks.  
It is designed to demonstrate a real-world layered architecture with proper exception handling, JWT session management, and a full test suite.

---

<a name="features-en"></a>
## Features

- **JWT Authentication** — access token + refresh token with rotation
- **Refresh Token Fingerprint** — `SHA-256(IP + User-Agent)` embedded in the refresh JWT to prevent token theft across different clients
- **Session Management** — every login creates a session row; logout revokes both tokens
- **Todo CRUD** — create, list, get, partial update (PATCH), full replace (PUT), soft-delete
- **Search / Filter / Sort / Paginate** — query by keyword, `is_completed`, `priority`, `due_from`, `due_to`; sort by any field; paginate with `page` + `page_size`
- **Soft Delete** — tasks are hidden, not physically removed
- **Custom Exception Hierarchy** — consistent JSON error shape across all errors
- **OpenAPI / Swagger** — every endpoint has `summary`, `description`, `response_model`, `status_code`, and examples
- **Database Indexes** — `owner_id` and composite `(owner_id, is_completed)` for fast queries
- **Alembic Migrations** — versioned schema evolution
- **Pytest Test Suite** — 32 tests with isolated test database and nested transactions

---

<a name="requirements-en"></a>
## Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| PostgreSQL | 13+ |
| pip | latest |

Key dependencies (see `requirements.txt` for the full list):

- `fastapi` 0.141+
- `sqlalchemy` 2.0+
- `alembic` 1.18+
- `pydantic` 2.13+
- `pyjwt` 2.13+
- `passlib[bcrypt]`
- `psycopg2-binary`
- `python-dotenv`
- `pytest`, `pytest-asyncio`

---

<a name="configuration-en"></a>
## Configuration

Copy the sample and fill in your values:

```bash
cp app/.env.example app/.env
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | — | Main PostgreSQL connection string |
| `TEST_DATABASE_URL` | ✅ | — | Separate DB used only during pytest |
| `AUTH_JWT_SECRET_KEY` | ✅ | `change me` | Secret for signing JWTs — use a long random string in production |
| `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES` | | `10` | Access token lifetime |
| `AUTH_REFRESH_TOKEN_EXPIRE_DAYS` | | `30` | Refresh token lifetime |
| `TIMEZONE` | | `Asia/Tehran` | Used for `due_date` validation |

**Example `app/.env`:**

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/todo
TEST_DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/todo_test

AUTH_JWT_SECRET_KEY=your-very-long-random-secret
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=10
AUTH_REFRESH_TOKEN_EXPIRE_DAYS=30
```

---

<a name="installation-en"></a>
## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/fastapi-todo-api.git
cd fastapi-todo-api

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp app/.env.example app/.env
# edit app/.env with your database credentials and secret key

# 5. Create databases in PostgreSQL
psql -U postgres -c "CREATE DATABASE todo;"
psql -U postgres -c "CREATE DATABASE todo_test;"

# 6. Run database migrations
cd app
TESTING=false alembic upgrade head

# 7. Start the development server
cd ..
uvicorn app.main:app --reload --app-dir app
```

The API will be available at `http://127.0.0.1:8000`.

---

<a name="usage-en"></a>
## Usage

### Basic workflow

```
1. POST /api/v1/auth/register   – create an account
2. POST /api/v1/auth/login      – get access + refresh tokens
3. Use Authorization: Bearer <access_token> on all /todos and /users endpoints
4. POST /api/v1/auth/refresh    – rotate tokens (same User-Agent required)
5. POST /api/v1/auth/logout     – revoke session
```

### Todo endpoints

```
POST   /api/v1/todos            Create a task
GET    /api/v1/todos            List tasks (search/filter/sort/paginate)
GET    /api/v1/todos/{id}       Get a single task
PATCH  /api/v1/todos/{id}       Partial update
PUT    /api/v1/todos/{id}       Full replace
DELETE /api/v1/todos/{id}       Soft-delete
```

<a name="seed-en"></a>
### Seed fake data

```bash
cd app
python scripts/seed.py
```

Generates fake users and tasks using `Faker`.

<a name="documentation-en"></a>
### Documentation

Interactive Swagger UI is available at:

```
http://127.0.0.1:8000/docs
```

ReDoc alternative:

```
http://127.0.0.1:8000/redoc
```

<a name="testing-en"></a>
### Testing

Make sure `TEST_DATABASE_URL` is set in `app/.env`, then:

```bash
# Apply migrations to the test database
cd app && TESTING=true alembic upgrade head && cd ..

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run only auth tests
pytest tests/test_auth.py -v
```

All 32 tests run against an isolated test database using nested transactions — each test rolls back automatically.

<a name="lint-en"></a>
### Lint and Reformat

The project uses **Ruff** for linting and formatting:

```bash
# Check for lint errors
ruff check app/

# Auto-fix
ruff check app/ --fix

# Format code
ruff format app/
```

---

<a name="structure-en"></a>
## Project Structure

```
fastapi-todo-api/
│
├── app/
│   ├── main.py                     FastAPI app entry point + exception handlers
│   ├── .env                        Environment variables (git-ignored)
│   ├── .env.example                Template for environment variables
│   │
│   ├── api/
│   │   ├── routers.py              Aggregates all versioned routers
│   │   └── v1/
│   │       ├── openapi_examples.py Centralized Swagger response examples
│   │       └── routes/
│   │           ├── auth.py         register / login / refresh / logout
│   │           ├── todos.py        CRUD + search/filter/sort/paginate
│   │           └── users.py        GET /me
│   │
│   ├── core/
│   │   ├── config.py               Pydantic settings (reads .env)
│   │   ├── database.py             SQLAlchemy engine + session + get_db
│   │   ├── exceptions.py           Custom exception classes + handlers
│   │   └── security.py             JWT generate/decode + fingerprint hash
│   │
│   ├── dependencies/
│   │   ├── auth.py                 get_current_user, get_auth_service
│   │   └── task.py                 get_task_service
│   │
│   ├── messages/
│   │   ├── auth.py                 Auth-related string constants
│   │   └── task.py                 Task-related string constants
│   │
│   ├── migrations/
│   │   ├── env.py                  Alembic environment configuration
│   │   └── versions/               Migration files
│   │
│   ├── models/
│   │   ├── base.py                 BaseModel (id, timestamps, soft-delete)
│   │   ├── user.py                 UserModel
│   │   ├── task.py                 TaskModel (with indexes)
│   │   └── session.py              SessionModel
│   │
│   ├── repositories/
│   │   ├── user_repository.py      DB queries for users
│   │   ├── task_repository.py      DB queries for tasks (search/filter/sort)
│   │   └── session_repository.py  DB queries for sessions
│   │
│   ├── schemas/
│   │   ├── auth.py                 Request/response schemas for auth
│   │   ├── task.py                 Request/response/query schemas for tasks
│   │   └── user.py                 User response schema
│   │
│   ├── scripts/
│   │   └── seed.py                 Fake data generator
│   │
│   └── services/
│       ├── auth_service.py         Auth business logic
│       └── task_service.py         Task business logic
│
├── docs/
│   ├── flows.md                    All application flows documented
│   └── flow-session.md             Session lifecycle diagram
│
├── tests/
│   ├── conftest.py                 Test DB setup, fixtures, authenticated clients
│   ├── test_auth.py                Auth endpoint tests (17 tests)
│   └── test_todos.py               Todo endpoint tests (15 tests)
│
├── requirements.txt
├── pyproject.toml                  Ruff + Pytest configuration
└── README.md
```

---

<a name="architecture-en"></a>
## Architecture

The project follows a **layered architecture**:

```
Request
  └─ Route (FastAPI)
       └─ Service (business logic)
            └─ Repository (data access)
                 └─ SQLAlchemy ORM
                      └─ PostgreSQL
```

| Layer | Responsibility |
|-------|----------------|
| **Routes** | HTTP handling, request validation, response serialization |
| **Services** | Business rules, orchestration, error decisions |
| **Repositories** | All DB queries — no business logic |
| **Models** | SQLAlchemy ORM table definitions |
| **Schemas** | Pydantic validation and serialization |

**Exception flow:**

All custom exceptions extend `BaseAppException` and are caught by `app_exception_handler`, which returns a consistent shape:

```json
{
  "success": false,
  "error": {
    "code": "TODO_NOT_FOUND",
    "message": "Todo not found"
  }
}
```

---

<a name="known-issues-en"></a>
## Known Issues

- Repositories use `async def` wrappers over synchronous SQLAlchemy — there is no real async I/O. A future version should migrate to `asyncpg` + `SQLAlchemy async`.
- `get_db` does not call `db.rollback()` on exception — a failed write can leave a dirty session in edge cases.
- No rate limiting — endpoints are unprotected against brute-force attacks.
- No Docker setup — deployment requires manual environment configuration.

---

<a name="license-en"></a>
## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

---

<a name="persian-version"></a>

# FastAPI Todo API 🇮🇷

یک REST API آماده برای مدیریت وظایف شخصی، ساخته‌شده با **FastAPI**، **SQLAlchemy**، **PostgreSQL** و **JWT** بر پایه معماری لایه‌بندی‌شده.

- [معرفی](#overview-fa)
- [ویژگی‌ها](#features-fa)
- [پیش‌نیازها](#requirements-fa)
- [تنظیمات](#configuration-fa)
- [نصب و راه‌اندازی](#installation-fa)
- [نحوه استفاده](#usage-fa)
  - [داده‌های آزمایشی](#seed-fa)
  - [مستندات](#documentation-fa)
  - [تست‌ها](#testing-fa)
  - [لینت و فرمت کد](#lint-fa)
- [ساختار پروژه](#structure-fa)
- [معماری](#architecture-fa)
- [مشکلات شناخته‌شده](#known-issues-fa)
- [لایسنس](#license-fa)

---

<a name="overview-fa"></a>
## معرفی

FastAPI Todo API یک سرویس بک‌اند است که به کاربران احراز هویت‌شده امکان ایجاد، مشاهده، به‌روزرسانی، حذف و جستجوی وظایف شخصی را می‌دهد.  
این پروژه برای نمایش معماری لایه‌بندی‌شده واقعی با مدیریت خطای یکپارچه، مدیریت session با JWT و مجموعه‌ای کامل از تست‌ها طراحی شده است.

---

<a name="features-fa"></a>
## ویژگی‌ها

- **احراز هویت JWT** — access token + refresh token با rotation خودکار
- **Fingerprint در Refresh Token** — `SHA-256(IP + User-Agent)` درون JWT جاسازی می‌شود تا از سرقت token جلوگیری کند
- **مدیریت Session** — هر ورود یک session ایجاد می‌کند؛ logout هر دو token را ابطال می‌کند
- **CRUD کامل Todo** — ایجاد، لیست، دریافت تکی، به‌روزرسانی جزئی (PATCH)، جایگزینی کامل (PUT)، حذف نرم
- **جستجو / فیلتر / مرتب‌سازی / صفحه‌بندی** — جستجو در عنوان و توضیحات، فیلتر وضعیت و اولویت و تاریخ
- **Soft Delete** — تسک‌ها از دید کاربر پنهان می‌شوند اما از دیتابیس حذف نمی‌شوند
- **سلسله‌مراتب خطا** — فرمت JSON یکسان برای تمام خطاها
- **OpenAPI / Swagger** — هر endpoint دارای `summary`، `description`، `response_model` و مثال است
- **Index دیتابیس** — روی `owner_id` و `(owner_id, is_completed)` برای کارایی بیشتر
- **Alembic Migrations** — مدیریت تغییرات schema
- **مجموعه تست Pytest** — 32 تست با دیتابیس مجزا و تراکنش‌های تودرتو

---

<a name="requirements-fa"></a>
## پیش‌نیازها

| پیش‌نیاز | نسخه |
|----------|------|
| Python | 3.10+ |
| PostgreSQL | 13+ |
| pip | آخرین نسخه |

وابستگی‌های اصلی (لیست کامل در `requirements.txt`):

- `fastapi` 0.141+
- `sqlalchemy` 2.0+
- `alembic` 1.18+
- `pydantic` 2.13+
- `pyjwt` 2.13+
- `passlib[bcrypt]`
- `psycopg2-binary`
- `python-dotenv`
- `pytest`, `pytest-asyncio`

---

<a name="configuration-fa"></a>
## تنظیمات

فایل نمونه را کپی کنید و مقادیر را پر کنید:

```bash
cp app/.env.example app/.env
```

| متغیر | اجباری | پیش‌فرض | توضیح |
|-------|--------|---------|-------|
| `DATABASE_URL` | ✅ | — | آدرس اتصال به PostgreSQL اصلی |
| `TEST_DATABASE_URL` | ✅ | — | دیتابیس جداگانه برای pytest |
| `AUTH_JWT_SECRET_KEY` | ✅ | `change me` | کلید امضای JWT — در production از یک رشته تصادفی طولانی استفاده کنید |
| `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES` | | `10` | مدت اعتبار access token |
| `AUTH_REFRESH_TOKEN_EXPIRE_DAYS` | | `30` | مدت اعتبار refresh token |
| `TIMEZONE` | | `Asia/Tehran` | برای اعتبارسنجی `due_date` |

**نمونه `app/.env`:**

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/todo
TEST_DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/todo_test

AUTH_JWT_SECRET_KEY=your-very-long-random-secret
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=10
AUTH_REFRESH_TOKEN_EXPIRE_DAYS=30
```

---

<a name="installation-fa"></a>
## نصب و راه‌اندازی

```bash
# ۱. دریافت پروژه
git clone https://github.com/your-username/fastapi-todo-api.git
cd fastapi-todo-api

# ۲. ساخت و فعال‌سازی محیط مجازی
python -m venv venv
source venv/bin/activate        # ویندوز: venv\Scripts\activate

# ۳. نصب وابستگی‌ها
pip install -r requirements.txt

# ۴. تنظیم متغیرهای محیطی
cp app/.env.example app/.env
# فایل app/.env را ویرایش کنید

# ۵. ساخت دیتابیس‌ها در PostgreSQL
psql -U postgres -c "CREATE DATABASE todo;"
psql -U postgres -c "CREATE DATABASE todo_test;"

# ۶. اجرای migration
cd app
TESTING=false alembic upgrade head

# ۷. اجرای سرور توسعه
cd ..
uvicorn app.main:app --reload --app-dir app
```

API در آدرس `http://127.0.0.1:8000` در دسترس خواهد بود.

---

<a name="usage-fa"></a>
## نحوه استفاده

### جریان اصلی

```
۱. POST /api/v1/auth/register   – ثبت‌نام
۲. POST /api/v1/auth/login      – ورود و دریافت توکن‌ها
۳. Authorization: Bearer <access_token> در همه درخواست‌های /todos و /users
۴. POST /api/v1/auth/refresh    – تجدید توکن (User-Agent باید یکسان باشد)
۵. POST /api/v1/auth/logout     – خروج و ابطال session
```

### endpoint های Todo

```
POST   /api/v1/todos            ایجاد تسک
GET    /api/v1/todos            لیست تسک‌ها (جستجو/فیلتر/مرتب‌سازی/صفحه‌بندی)
GET    /api/v1/todos/{id}       دریافت یک تسک
PATCH  /api/v1/todos/{id}       به‌روزرسانی جزئی
PUT    /api/v1/todos/{id}       جایگزینی کامل
DELETE /api/v1/todos/{id}       حذف نرم
```

<a name="seed-fa"></a>
### داده‌های آزمایشی

```bash
cd app
python scripts/seed.py
```

با استفاده از `Faker` کاربران و تسک‌های ساختگی تولید می‌کند.

<a name="documentation-fa"></a>
### مستندات

Swagger UI تعاملی:

```
http://127.0.0.1:8000/docs
```

نسخه ReDoc:

```
http://127.0.0.1:8000/redoc
```

<a name="testing-fa"></a>
### تست‌ها

مطمئن شوید `TEST_DATABASE_URL` در `app/.env` تنظیم شده، سپس:

```bash
# اعمال migration روی دیتابیس تست
cd app && TESTING=true alembic upgrade head && cd ..

# اجرای همه تست‌ها
pytest

# با جزئیات بیشتر
pytest -v

# فقط تست‌های auth
pytest tests/test_auth.py -v
```

تمام 32 تست روی دیتابیس مجزا با تراکنش‌های تودرتو اجرا می‌شوند — هر تست به صورت خودکار rollback می‌شود.

<a name="lint-fa"></a>
### لینت و فرمت کد

پروژه از **Ruff** استفاده می‌کند:

```bash
# بررسی خطاهای lint
ruff check app/

# رفع خودکار
ruff check app/ --fix

# فرمت‌بندی کد
ruff format app/
```

---

<a name="structure-fa"></a>
## ساختار پروژه

```
fastapi-todo-api/
│
├── app/
│   ├── main.py                     نقطه ورود FastAPI + ثبت exception handler ها
│   ├── .env                        متغیرهای محیطی (در git نادیده گرفته می‌شود)
│   ├── .env.example                نمونه متغیرهای محیطی
│   │
│   ├── api/
│   │   ├── routers.py              جمع‌آوری همه router های نسخه‌بندی‌شده
│   │   └── v1/
│   │       ├── openapi_examples.py مثال‌های Swagger به صورت متمرکز
│   │       └── routes/
│   │           ├── auth.py         register / login / refresh / logout
│   │           ├── todos.py        CRUD + جستجو/فیلتر/مرتب‌سازی/صفحه‌بندی
│   │           └── users.py        GET /me
│   │
│   ├── core/
│   │   ├── config.py               تنظیمات Pydantic (خواندن از .env)
│   │   ├── database.py             SQLAlchemy engine + session + get_db
│   │   ├── exceptions.py           کلاس‌های استثنا + handler های سراسری
│   │   └── security.py             تولید/decode JWT + ساخت fingerprint
│   │
│   ├── dependencies/               وابستگی‌های FastAPI (get_current_user و ...)
│   ├── messages/                   ثابت‌های متنی پیام‌ها
│   ├── migrations/                 فایل‌های Alembic
│   ├── models/                     مدل‌های SQLAlchemy ORM
│   ├── repositories/               لایه دسترسی به داده
│   ├── schemas/                    اسکیماهای Pydantic
│   ├── scripts/                    اسکریپت seed داده‌های آزمایشی
│   └── services/                   منطق کسب‌وکار
│
├── docs/
│   ├── flows.md                    مستند همه جریان‌های برنامه
│   └── flow-session.md             نمودار چرخه حیات session
│
├── tests/
│   ├── conftest.py                 راه‌اندازی دیتابیس تست و fixture ها
│   ├── test_auth.py                تست‌های احراز هویت (17 تست)
│   └── test_todos.py               تست‌های Todo (15 تست)
│
├── requirements.txt
├── pyproject.toml                  تنظیمات Ruff و Pytest
└── README.md
```

---

<a name="architecture-fa"></a>
## معماری

پروژه از **معماری لایه‌بندی‌شده** پیروی می‌کند:

```
درخواست HTTP
  └─ Route (FastAPI)
       └─ Service (منطق کسب‌وکار)
            └─ Repository (دسترسی به داده)
                 └─ SQLAlchemy ORM
                      └─ PostgreSQL
```

| لایه | مسئولیت |
|------|---------|
| **Routes** | مدیریت HTTP، اعتبارسنجی ورودی، سریال‌سازی خروجی |
| **Services** | قوانین کسب‌وکار، هماهنگی، تصمیم‌گیری در مورد خطا |
| **Repositories** | تمام query های دیتابیس — بدون منطق کسب‌وکار |
| **Models** | تعریف جداول ORM |
| **Schemas** | اعتبارسنجی و سریال‌سازی Pydantic |

**فرمت یکسان خطاها:**

```json
{
  "success": false,
  "error": {
    "code": "TODO_NOT_FOUND",
    "message": "Todo not found"
  }
}
```

---

<a name="known-issues-fa"></a>
## مشکلات شناخته‌شده

- Repository ها از `async def` روی SQLAlchemy همزمان استفاده می‌کنند — در واقع I/O غیرهمزمان وجود ندارد. نسخه آینده باید به `asyncpg` مهاجرت کند.
- `get_db` در صورت خطا `db.rollback()` صدا نمی‌زند.
- Rate limiting پیاده‌سازی نشده.
- Docker setup وجود ندارد.

---

<a name="license-fa"></a>
## لایسنس

این پروژه تحت **مجوز MIT** منتشر شده است. فایل [LICENSE](LICENSE) را ببینید.

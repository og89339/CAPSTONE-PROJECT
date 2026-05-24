# Course Enrollment Platform API

A secure, database-backed RESTful API built with FastAPI for managing course enrollments. The system implements JWT authentication, role-based access control (RBAC), and comprehensive business rules for course enrollment management.

## Features

- **Authentication & Authorization**: JWT-based authentication with secure password hashing
- **Role-Based Access Control**: Separate permissions for students and administrators
- **User Management**: Register, login, and profile retrieval
- **Course Management**: Full CRUD operations with admin-only write access
- **Enrollment Management**: Enroll/deregister with business rule validation
- **Administrative Oversight**: View all enrollments, manage student registrations
- **Database Migrations**: Alembic for schema versioning
- **Comprehensive Testing**: Full test coverage for all endpoints

## Technology Stack

- **Framework**: FastAPI
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose) + bcrypt password hashing
- **Validation**: Pydantic v2
- **Testing**: pytest with httpx TestClient

## Project Structure

```
course-enrollment-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Application settings
│   ├── database.py          # Database connection and session
│   ├── models.py            # SQLAlchemy models
│   ├── dependencies.py      # FastAPI dependencies (auth, RBAC)
│   ├── schemas/             # Pydantic request/response models
│   │   ├── user.py
│   │   ├── course.py
│   │   └── enrollment.py
│   ├── routers/             # API route handlers
│   │   ├── auth.py          # Authentication routes
│   │   ├── users.py         # User profile routes
│   │   ├── courses.py       # Course management routes
│   │   └── enrollments.py   # Enrollment management routes
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py
│   │   ├── course_service.py
│   │   └── enrollment_service.py
│   ├── repository/          # Database access layer
│   │   ├── user_repo.py
│   │   ├── course_repo.py
│   │   └── enrollment_repo.py
│   └── utils/
│       └── security.py      # JWT and password utilities
├── tests/                   # Test suite
│   ├── conftest.py          # Test fixtures
│   ├── test_auth.py         # Authentication tests
│   ├── test_users.py        # User management tests
│   ├── test_courses.py      # Course management tests
│   └── test_enrollments.py  # Enrollment tests
├── alembic/                 # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_migration.py
├── requirements.txt         # Python dependencies
├── alembic.ini             # Alembic configuration
└── README.md               # This file
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- pip or virtualenv

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd course-enrollment-api
```

2. **Create and activate a virtual environment**

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables (optional)**

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite:///./course_enrollment.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

For production with PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost/course_enrollment
SECRET_KEY=your-production-secret-key
```

## Running Migrations

### Initialize the database (first time only)

```bash
alembic upgrade head
```

### Create a new migration (after model changes)

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback migrations

```bash
alembic downgrade -1
```

## Running the Application

### Development mode

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Interactive API documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

- ## Live Demo

The API is deployed and accessible at:

- **Base URL**: https://course-enrollment-api-n7dh.onrender.com/
- **Interactive API Docs (Swagger UI)**: https://course-enrollment-api-n7dh.onrender.com/docs
- **Courses Endpoint**: https://course-enrollment-api-n7dh.onrender.com/api/courses/

> **Note**: The free Render tier may spin down after periods of inactivity. The first request might take 30–50 seconds to wake up the service.

### Production mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Running Tests

### Run all tests

```bash
pytest
```

### Run with verbose output

```bash
pytest -v
```

### Run specific test file

```bash
pytest tests/test_auth.py
```

### Run with coverage report

```bash
pytest --cov=app --cov-report=html
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/auth/register` | Register a new user | Public |
| POST | `/api/auth/login` | Login and get JWT token | Public |

### Users

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/users/profile` | Get current user profile | Authenticated |

### Courses

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/courses/` | List all active courses | Public |
| GET | `/api/courses/{id}` | Get course details | Public |
| POST | `/api/courses/` | Create a course | Admin only |
| PUT | `/api/courses/{id}` | Update a course | Admin only |
| DELETE | `/api/courses/{id}` | Delete a course | Admin only |
| PATCH | `/api/courses/{id}/activate` | Activate a course | Admin only |
| PATCH | `/api/courses/{id}/deactivate` | Deactivate a course | Admin only |

### Enrollments

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/enrollments/` | Enroll in a course | Student only |
| DELETE | `/api/enrollments/course/{id}` | Deregister from a course | Student only |
| GET | `/api/enrollments/my-enrollments` | View my enrollments | Student only |
| GET | `/api/enrollments/admin/all` | View all enrollments | Admin only |
| GET | `/api/enrollments/admin/course/{id}` | View course enrollments | Admin only |
| DELETE | `/api/enrollments/admin/{id}` | Remove a student from course | Admin only |

## Role-Based Access Control

| Action | Student | Admin |
|--------|---------|-------|
| View courses | Yes | Yes |
| Enroll in course | Yes | No |
| Deregister from course | Yes | No |
| Create course | No | Yes |
| Update course | No | Yes |
| Delete course | No | Yes |
| View all enrollments | No | Yes |

## Authentication

The API uses JWT Bearer tokens. To authenticate:

1. Register a user via `POST /api/auth/register`
2. Login via `POST /api/auth/login` to receive a token
3. Include the token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

## Business Rules

### User Management
- Email must be unique
- Role must be either "student" or "admin"
- Inactive users cannot authenticate
- Passwords are securely hashed with bcrypt

### Course Management
- Course code must be unique
- Capacity must be greater than zero
- Only admins can create, update, or delete courses
- Deactivated courses are hidden from public listings

### Enrollment Management
- Only authenticated students can enroll
- A student cannot enroll in the same course twice
- Enrollment fails if the course is at full capacity
- Enrollment fails if the course is inactive
- Students can deregister from courses they are enrolled in
- Admins can view all enrollments and remove students from courses

## Validation & Error Handling

All incoming data is validated using Pydantic schemas. The API returns consistent error responses:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors, business rule violations)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (Pydantic validation errors)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./course_enrollment.db` |
| `SECRET_KEY` | JWT signing secret | `your-secret-key-change-in-production` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | `30` |

## License

This project is for educational purposes.

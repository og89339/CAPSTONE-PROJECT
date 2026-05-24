import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.utils.security import hash_password, create_access_token
from app.models import User, Course, Enrollment

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_student(db):
    user = User(
        name="Test Student",
        email="student@test.com",
        hashed_password=hash_password("password123"),
        role="student",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db):
    user = User(
        name="Test Admin",
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        role="admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def inactive_user(db):
    user = User(
        name="Inactive User",
        email="inactive@test.com",
        hashed_password=hash_password("password123"),
        role="student",
        is_active=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_course(db):
    course = Course(
        title="Test Course",
        code="TEST101",
        capacity=30,
        is_active=True
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@pytest.fixture
def test_course_full(db):
    course = Course(
        title="Full Course",
        code="FULL101",
        capacity=1,
        is_active=True
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@pytest.fixture
def inactive_course(db):
    course = Course(
        title="Inactive Course",
        code="INACT101",
        capacity=30,
        is_active=False
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@pytest.fixture
def student_token(test_student):
    token = create_access_token(data={"sub": str(test_student.id), "email": test_student.email, "role": test_student.role})
    return token


@pytest.fixture
def admin_token(test_admin):
    token = create_access_token(data={"sub": str(test_admin.id), "email": test_admin.email, "role": test_admin.role})
    return token


@pytest.fixture
def student_headers(student_token):
    return {"Authorization": f"Bearer {student_token}"}


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

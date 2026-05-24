import pytest


class TestAuthRegister:
    """Tests for user registration endpoint: POST /api/auth/register"""

    def test_register_student_success(self, client):
        """Successfully register a new student user"""
        response = client.post("/api/auth/register", json={
            "name": "New Student",
            "email": "newstudent@test.com",
            "password": "password123",
            "role": "student"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newstudent@test.com"
        assert data["name"] == "New Student"
        assert data["role"] == "student"
        assert data["is_active"] == True
        assert "id" in data

    def test_register_admin_success(self, client):
        """Successfully register a new admin user"""
        response = client.post("/api/auth/register", json={
            "name": "New Admin",
            "email": "newadmin@test.com",
            "password": "password123",
            "role": "admin"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "admin"

    def test_register_duplicate_email(self, client, test_student):
        """Fail to register with duplicate email"""
        response = client.post("/api/auth/register", json={
            "name": "Another Student",
            "email": test_student.email,
            "password": "password123",
            "role": "student"
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        """Fail to register with invalid email format"""
        response = client.post("/api/auth/register", json={
            "name": "Test",
            "email": "invalid-email",
            "password": "password123",
            "role": "student"
        })
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """Fail to register with password less than 6 characters"""
        response = client.post("/api/auth/register", json={
            "name": "Test",
            "email": "shortpass@test.com",
            "password": "123",
            "role": "student"
        })
        assert response.status_code == 422

    def test_register_invalid_role(self, client):
        """Fail to register with invalid role"""
        response = client.post("/api/auth/register", json={
            "name": "Test",
            "email": "role@test.com",
            "password": "password123",
            "role": "teacher"
        })
        assert response.status_code == 422

    def test_register_missing_name(self, client):
        """Fail to register without name field"""
        response = client.post("/api/auth/register", json={
            "email": "noname@test.com",
            "password": "password123"
        })
        assert response.status_code == 422

    def test_register_missing_password(self, client):
        """Fail to register without password field"""
        response = client.post("/api/auth/register", json={
            "name": "Test",
            "email": "nopass@test.com"
        })
        assert response.status_code == 422


class TestAuthLogin:
    """Tests for user login endpoint: POST /api/auth/login"""

    def test_login_success(self, client, test_student):
        """Successfully login with valid credentials"""
        response = client.post("/api/auth/login", json={
            "email": test_student.email,
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_admin_success(self, client, test_admin):
        """Successfully login as admin"""
        response = client.post("/api/auth/login", json={
            "email": test_admin.email,
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_invalid_email(self, client):
        """Fail to login with non-existent email"""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "password123"
        })
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_invalid_password(self, client, test_student):
        """Fail to login with wrong password"""
        response = client.post("/api/auth/login", json={
            "email": test_student.email,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_inactive_user(self, client, inactive_user):
        """Fail to login with inactive user account"""
        response = client.post("/api/auth/login", json={
            "email": inactive_user.email,
            "password": "password123"
        })
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()

    def test_login_invalid_email_format(self, client):
        """Fail to login with invalid email format"""
        response = client.post("/api/auth/login", json={
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 422

    def test_login_missing_email(self, client):
        """Fail to login without email"""
        response = client.post("/api/auth/login", json={
            "password": "password123"
        })
        assert response.status_code == 422

    def test_login_missing_password(self, client):
        """Fail to login without password"""
        response = client.post("/api/auth/login", json={
            "email": "test@test.com"
        })
        assert response.status_code == 422

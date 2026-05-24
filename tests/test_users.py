import pytest


class TestUserProfile:
    """Tests for user profile endpoint: GET /api/users/profile"""

    def test_get_profile_authenticated_student(self, client, test_student, student_headers):
        """Student can retrieve their own profile"""
        response = client.get("/api/users/profile", headers=student_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_student.id
        assert data["name"] == test_student.name
        assert data["email"] == test_student.email
        assert data["role"] == "student"
        assert data["is_active"] == True

    def test_get_profile_authenticated_admin(self, client, test_admin, admin_headers):
        """Admin can retrieve their own profile"""
        response = client.get("/api/users/profile", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_admin.id
        assert data["role"] == "admin"

    def test_get_profile_no_token(self, client):
        """Fail to get profile without authentication token"""
        response = client.get("/api/users/profile")
        assert response.status_code == 401

    def test_get_profile_invalid_token(self, client):
        """Fail to get profile with invalid token"""
        response = client.get("/api/users/profile", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert response.status_code == 401

    def test_get_profile_expired_token(self, client):
        """Fail to get profile with expired/malformed token"""
        response = client.get("/api/users/profile", headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxfQ.WCJ1"
        })
        assert response.status_code == 401

    def test_profile_response_structure(self, client, student_headers):
        """Verify profile response has correct structure and types"""
        response = client.get("/api/users/profile", headers=student_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(key in data for key in ["id", "name", "email", "role", "is_active"])
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["email"], str)
        assert isinstance(data["role"], str)
        assert isinstance(data["is_active"], bool)

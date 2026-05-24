import pytest


class TestCourseList:
    """Tests for listing courses: GET /api/courses/"""

    def test_list_courses_public(self, client, test_course):
        """Anyone can list active courses without authentication"""
        response = client.get("/api/courses/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["title"] == test_course.title

    def test_list_courses_does_not_show_inactive(self, client, inactive_course):
        """Inactive courses should not appear in public list"""
        response = client.get("/api/courses/")
        assert response.status_code == 200
        data = response.json()
        course_codes = [c["code"] for c in data]
        assert inactive_course.code not in course_codes

    def test_list_courses_empty(self, client):
        """List courses returns empty list when no active courses"""
        response = client.get("/api/courses/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_courses_includes_enrollment_count(self, client, test_course):
        """Course list includes enrollment count and available slots"""
        response = client.get("/api/courses/")
        assert response.status_code == 200
        data = response.json()
        assert "enrollment_count" in data[0]
        assert "available_slots" in data[0]
        assert data[0]["enrollment_count"] == 0
        assert data[0]["available_slots"] == test_course.capacity


class TestCourseDetail:
    """Tests for getting course details: GET /api/courses/{course_id}"""

    def test_get_course_public(self, client, test_course):
        """Anyone can get course details without authentication"""
        response = client.get(f"/api/courses/{test_course.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_course.id
        assert data["title"] == test_course.title
        assert data["code"] == test_course.code
        assert data["capacity"] == test_course.capacity

    def test_get_course_not_found(self, client):
        """Get non-existent course returns 404"""
        response = client.get("/api/courses/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_course_includes_enrollment_count(self, client, test_course):
        """Course detail includes enrollment metrics"""
        response = client.get(f"/api/courses/{test_course.id}")
        assert response.status_code == 200
        data = response.json()
        assert "enrollment_count" in data
        assert "available_slots" in data


class TestCourseCreate:
    """Tests for creating courses: POST /api/courses/ (admin only)"""

    def test_create_course_admin(self, client, admin_headers):
        """Admin can create a course"""
        response = client.post("/api/courses/", json={
            "title": "New Course",
            "code": "NEW101",
            "capacity": 25
        }, headers=admin_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Course"
        assert data["code"] == "NEW101"
        assert data["capacity"] == 25
        assert data["is_active"] == True

    def test_create_course_student_forbidden(self, client, student_headers):
        """Student cannot create a course"""
        response = client.post("/api/courses/", json={
            "title": "New Course",
            "code": "STU101",
            "capacity": 25
        }, headers=student_headers)
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()

    def test_create_course_no_auth(self, client):
        """Unauthenticated user cannot create a course"""
        response = client.post("/api/courses/", json={
            "title": "New Course",
            "code": "NOAUTH101",
            "capacity": 25
        })
        assert response.status_code == 401

    def test_create_course_duplicate_code(self, client, admin_headers, test_course):
        """Cannot create course with duplicate code"""
        response = client.post("/api/courses/", json={
            "title": "Another Course",
            "code": test_course.code,
            "capacity": 25
        }, headers=admin_headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_course_zero_capacity(self, client, admin_headers):
        """Cannot create course with zero capacity"""
        response = client.post("/api/courses/", json={
            "title": "Bad Course",
            "code": "ZERO101",
            "capacity": 0
        }, headers=admin_headers)
        assert response.status_code == 422

    def test_create_course_negative_capacity(self, client, admin_headers):
        """Cannot create course with negative capacity"""
        response = client.post("/api/courses/", json={
            "title": "Bad Course",
            "code": "NEG101",
            "capacity": -5
        }, headers=admin_headers)
        assert response.status_code == 422

    def test_create_course_empty_title(self, client, admin_headers):
        """Cannot create course with empty title"""
        response = client.post("/api/courses/", json={
            "title": "",
            "code": "EMPTY101",
            "capacity": 25
        }, headers=admin_headers)
        assert response.status_code == 422

    def test_create_course_missing_fields(self, client, admin_headers):
        """Cannot create course without required fields"""
        response = client.post("/api/courses/", json={
            "title": "Only Title"
        }, headers=admin_headers)
        assert response.status_code == 422


class TestCourseUpdate:
    """Tests for updating courses: PUT /api/courses/{course_id} (admin only)"""

    def test_update_course_admin(self, client, admin_headers, test_course):
        """Admin can update a course"""
        response = client.put(f"/api/courses/{test_course.id}", json={
            "title": "Updated Title",
            "capacity": 50
        }, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["capacity"] == 50
        assert data["code"] == test_course.code  # unchanged

    def test_update_course_student_forbidden(self, client, student_headers, test_course):
        """Student cannot update a course"""
        response = client.put(f"/api/courses/{test_course.id}", json={
            "title": "Hacked Title"
        }, headers=student_headers)
        assert response.status_code == 403

    def test_update_course_no_auth(self, client, test_course):
        """Unauthenticated user cannot update a course"""
        response = client.put(f"/api/courses/{test_course.id}", json={
            "title": "Hacked Title"
        })
        assert response.status_code == 401

    def test_update_course_not_found(self, client, admin_headers):
        """Update non-existent course returns 404"""
        response = client.put("/api/courses/99999", json={
            "title": "Ghost Course"
        }, headers=admin_headers)
        assert response.status_code == 404

    def test_update_course_duplicate_code(self, client, db, admin_headers, test_course):
        """Cannot update course to a code that already exists"""
        # Create another course first
        from app.models import Course
        other = Course(title="Other", code="OTHER101", capacity=20)
        db.add(other)
        db.commit()

        response = client.put(f"/api/courses/{other.id}", json={
            "code": test_course.code
        }, headers=admin_headers)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_update_course_zero_capacity(self, client, admin_headers, test_course):
        """Cannot update course with zero capacity"""
        response = client.put(f"/api/courses/{test_course.id}", json={
            "capacity": 0
        }, headers=admin_headers)
        assert response.status_code == 422


class TestCourseDelete:
    """Tests for deleting courses: DELETE /api/courses/{course_id} (admin only)"""

    def test_delete_course_admin(self, client, admin_headers, test_course):
        """Admin can delete a course"""
        response = client.delete(f"/api/courses/{test_course.id}", headers=admin_headers)
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

    def test_delete_course_student_forbidden(self, client, student_headers, test_course):
        """Student cannot delete a course"""
        response = client.delete(f"/api/courses/{test_course.id}", headers=student_headers)
        assert response.status_code == 403

    def test_delete_course_no_auth(self, client, test_course):
        """Unauthenticated user cannot delete a course"""
        response = client.delete(f"/api/courses/{test_course.id}")
        assert response.status_code == 401

    def test_delete_course_not_found(self, client, admin_headers):
        """Delete non-existent course returns 404"""
        response = client.delete("/api/courses/99999", headers=admin_headers)
        assert response.status_code == 404


class TestCourseActivateDeactivate:
    """Tests for course activation/deactivation (admin only)"""

    def test_activate_course_admin(self, client, admin_headers, inactive_course):
        """Admin can activate a course"""
        response = client.patch(f"/api/courses/{inactive_course.id}/activate", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["is_active"] == True

    def test_deactivate_course_admin(self, client, admin_headers, test_course):
        """Admin can deactivate a course"""
        response = client.patch(f"/api/courses/{test_course.id}/deactivate", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["is_active"] == False

    def test_activate_course_student_forbidden(self, client, student_headers, inactive_course):
        """Student cannot activate a course"""
        response = client.patch(f"/api/courses/{inactive_course.id}/activate", headers=student_headers)
        assert response.status_code == 403

    def test_deactivate_course_student_forbidden(self, client, student_headers, test_course):
        """Student cannot deactivate a course"""
        response = client.patch(f"/api/courses/{test_course.id}/deactivate", headers=student_headers)
        assert response.status_code == 403

    def test_activate_course_not_found(self, client, admin_headers):
        """Activate non-existent course returns 404"""
        response = client.patch("/api/courses/99999/activate", headers=admin_headers)
        assert response.status_code == 404

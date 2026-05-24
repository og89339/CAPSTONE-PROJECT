import pytest


class TestEnrollStudent:
    """Tests for enrolling in courses: POST /api/enrollments/ (student only)"""

    def test_enroll_success(self, client, student_headers, test_course):
        """Student can successfully enroll in a course"""
        response = client.post("/api/enrollments/", json={
            "course_id": test_course.id
        }, headers=student_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["course_id"] == test_course.id
        assert "id" in data

    def test_enroll_admin_forbidden(self, client, admin_headers, test_course):
        """Admin cannot enroll in a course"""
        response = client.post("/api/enrollments/", json={
            "course_id": test_course.id
        }, headers=admin_headers)
        assert response.status_code == 403
        assert "student" in response.json()["detail"].lower()

    def test_enroll_no_auth(self, client, test_course):
        """Unauthenticated user cannot enroll"""
        response = client.post("/api/enrollments/", json={
            "course_id": test_course.id
        })
        assert response.status_code == 401

    def test_enroll_duplicate(self, client, student_headers, test_course, db):
        """Cannot enroll in the same course twice"""
        # First enrollment
        response = client.post("/api/enrollments/", json={
            "course_id": test_course.id
        }, headers=student_headers)
        assert response.status_code == 201

        # Second enrollment attempt
        response = client.post("/api/enrollments/", json={
            "course_id": test_course.id
        }, headers=student_headers)
        assert response.status_code == 400
        assert "already enrolled" in response.json()["detail"].lower()

    def test_enroll_course_full(self, client, student_headers, test_course_full, db):
        """Cannot enroll in a full course"""
        # Fill the course first
        from app.models import User, Enrollment
        other_user = User(name="Other", email="other@test.com", hashed_password="hashed", role="student")
        db.add(other_user)
        db.commit()
        enrollment = Enrollment(user_id=other_user.id, course_id=test_course_full.id)
        db.add(enrollment)
        db.commit()

        # Try to enroll
        response = client.post("/api/enrollments/", json={
            "course_id": test_course_full.id
        }, headers=student_headers)
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()

    def test_enroll_inactive_course(self, client, student_headers, inactive_course):
        """Cannot enroll in an inactive course"""
        response = client.post("/api/enrollments/", json={
            "course_id": inactive_course.id
        }, headers=student_headers)
        assert response.status_code == 400
        assert "not active" in response.json()["detail"].lower()

    def test_enroll_course_not_found(self, client, student_headers):
        """Cannot enroll in non-existent course"""
        response = client.post("/api/enrollments/", json={
            "course_id": 99999
        }, headers=student_headers)
        assert response.status_code == 404

    def test_enroll_missing_course_id(self, client, student_headers):
        """Cannot enroll without course_id"""
        response = client.post("/api/enrollments/", json={}, headers=student_headers)
        assert response.status_code == 422


class TestDeregisterStudent:
    """Tests for deregistering from courses: DELETE /api/enrollments/course/{course_id} (student only)"""

    def test_deregister_success(self, client, student_headers, test_course, db, test_student):
        """Student can deregister from a course"""
        # Enroll first
        from app.models import Enrollment
        enrollment = Enrollment(user_id=test_student.id, course_id=test_course.id)
        db.add(enrollment)
        db.commit()

        # Deregister
        response = client.delete(f"/api/enrollments/course/{test_course.id}", headers=student_headers)
        assert response.status_code == 200
        assert "deregistered" in response.json()["message"].lower()

    def test_deregister_admin_forbidden(self, client, admin_headers, test_course):
        """Admin cannot deregister from a course"""
        response = client.delete(f"/api/enrollments/course/{test_course.id}", headers=admin_headers)
        assert response.status_code == 403

    def test_deregister_no_auth(self, client, test_course):
        """Unauthenticated user cannot deregister"""
        response = client.delete(f"/api/enrollments/course/{test_course.id}")
        assert response.status_code == 401

    def test_deregister_not_enrolled(self, client, student_headers, test_course):
        """Cannot deregister from a course not enrolled in"""
        response = client.delete(f"/api/enrollments/course/{test_course.id}", headers=student_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_deregister_course_not_found(self, client, student_headers):
        """Cannot deregister from non-existent course"""
        response = client.delete("/api/enrollments/course/99999", headers=student_headers)
        assert response.status_code == 404


class TestGetMyEnrollments:
    """Tests for viewing own enrollments: GET /api/enrollments/my-enrollments (student only)"""

    def test_get_my_enrollments(self, client, student_headers, test_course, db, test_student):
        """Student can view their enrollments"""
        # Enroll first
        from app.models import Enrollment
        enrollment = Enrollment(user_id=test_student.id, course_id=test_course.id)
        db.add(enrollment)
        db.commit()

        response = client.get("/api/enrollments/my-enrollments", headers=student_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["user"]["id"] == test_student.id

    def test_get_my_enrollments_empty(self, client, student_headers):
        """Student with no enrollments gets empty list"""
        response = client.get("/api/enrollments/my-enrollments", headers=student_headers)
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_my_enrollments_admin_forbidden(self, client, admin_headers):
        """Admin cannot access student enrollments endpoint"""
        response = client.get("/api/enrollments/my-enrollments", headers=admin_headers)
        assert response.status_code == 403

    def test_get_my_enrollments_no_auth(self, client):
        """Unauthenticated user cannot view enrollments"""
        response = client.get("/api/enrollments/my-enrollments")
        assert response.status_code == 401


class TestAdminGetAllEnrollments:
    """Tests for admin viewing all enrollments: GET /api/enrollments/admin/all (admin only)"""

    def test_get_all_enrollments_admin(self, client, admin_headers, test_course, db, test_student):
        """Admin can view all enrollments"""
        # Create enrollment
        from app.models import Enrollment
        enrollment = Enrollment(user_id=test_student.id, course_id=test_course.id)
        db.add(enrollment)
        db.commit()

        response = client.get("/api/enrollments/admin/all", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "user" in data[0]
        assert "course" in data[0]

    def test_get_all_enrollments_student_forbidden(self, client, student_headers):
        """Student cannot view all enrollments"""
        response = client.get("/api/enrollments/admin/all", headers=student_headers)
        assert response.status_code == 403

    def test_get_all_enrollments_no_auth(self, client):
        """Unauthenticated user cannot view all enrollments"""
        response = client.get("/api/enrollments/admin/all")
        assert response.status_code == 401

    def test_get_all_enrollments_empty(self, client, admin_headers):
        """Admin gets empty list when no enrollments exist"""
        response = client.get("/api/enrollments/admin/all", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data == []


class TestAdminGetCourseEnrollments:
    """Tests for admin viewing course enrollments: GET /api/enrollments/admin/course/{course_id} (admin only)"""

    def test_get_course_enrollments_admin(self, client, admin_headers, test_course, db, test_student):
        """Admin can view enrollments for a specific course"""
        # Create enrollment
        from app.models import Enrollment
        enrollment = Enrollment(user_id=test_student.id, course_id=test_course.id)
        db.add(enrollment)
        db.commit()

        response = client.get(f"/api/enrollments/admin/course/{test_course.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["course"]["id"] == test_course.id

    def test_get_course_enrollments_student_forbidden(self, client, student_headers, test_course):
        """Student cannot view course enrollments"""
        response = client.get(f"/api/enrollments/admin/course/{test_course.id}", headers=student_headers)
        assert response.status_code == 403

    def test_get_course_enrollments_no_auth(self, client, test_course):
        """Unauthenticated user cannot view course enrollments"""
        response = client.get(f"/api/enrollments/admin/course/{test_course.id}")
        assert response.status_code == 401

    def test_get_course_enrollments_course_not_found(self, client, admin_headers):
        """Get enrollments for non-existent course returns 404"""
        response = client.get("/api/enrollments/admin/course/99999", headers=admin_headers)
        assert response.status_code == 404


class TestAdminRemoveEnrollment:
    """Tests for admin removing enrollments: DELETE /api/enrollments/admin/{enrollment_id} (admin only)"""

    def test_remove_enrollment_admin(self, client, admin_headers, test_course, db, test_student):
        """Admin can remove a student from a course"""
        # Create enrollment
        from app.models import Enrollment
        enrollment = Enrollment(user_id=test_student.id, course_id=test_course.id)
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)

        response = client.delete(f"/api/enrollments/admin/{enrollment.id}", headers=admin_headers)
        assert response.status_code == 200
        assert "removed" in response.json()["message"].lower()

    def test_remove_enrollment_student_forbidden(self, client, student_headers, test_course, db, test_student):
        """Student cannot remove an enrollment via admin endpoint"""
        from app.models import Enrollment
        enrollment = Enrollment(user_id=test_student.id, course_id=test_course.id)
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)

        response = client.delete(f"/api/enrollments/admin/{enrollment.id}", headers=student_headers)
        assert response.status_code == 403

    def test_remove_enrollment_no_auth(self, client, test_course, db, test_student):
        """Unauthenticated user cannot remove enrollment"""
        from app.models import Enrollment
        enrollment = Enrollment(user_id=test_student.id, course_id=test_course.id)
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)

        response = client.delete(f"/api/enrollments/admin/{enrollment.id}")
        assert response.status_code == 401

    def test_remove_enrollment_not_found(self, client, admin_headers):
        """Remove non-existent enrollment returns 404"""
        response = client.delete("/api/enrollments/admin/99999", headers=admin_headers)
        assert response.status_code == 404

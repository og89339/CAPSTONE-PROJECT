from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repository.enrollment_repo import EnrollmentRepository
from app.repository.course_repo import CourseRepository
from app.repository.user_repo import UserRepository
from typing import List


class EnrollmentService:
    def __init__(self, db: Session):
        self.db = db
        self.enrollment_repo = EnrollmentRepository(db)
        self.course_repo = CourseRepository(db)
        self.user_repo = UserRepository(db)

    def enroll_student(self, user_id: int, course_id: int):
        # Check if course exists and is active
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        if not course.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course is not active"
            )

        # Check if already enrolled
        if self.enrollment_repo.is_enrolled(user_id, course_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already enrolled in this course"
            )

        # Check if course is full
        if self.course_repo.is_full(course_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course is full"
            )

        enrollment = self.enrollment_repo.create(user_id=user_id, course_id=course_id)
        return enrollment

    def deregister_student(self, user_id: int, course_id: int):
        enrollment = self.enrollment_repo.get_by_user_and_course(user_id, course_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )

        self.enrollment_repo.delete(enrollment)
        return {"message": "Successfully deregistered from course"}

    def get_student_enrollments(self, user_id: int):
        return self.enrollment_repo.get_by_user(user_id)

    def get_all_enrollments(self):
        return self.enrollment_repo.get_all()

    def get_course_enrollments(self, course_id: int):
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        return self.enrollment_repo.get_by_course(course_id)

    def remove_student_from_course(self, enrollment_id: int):
        enrollment = self.enrollment_repo.get_by_id(enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found"
            )
        self.enrollment_repo.delete(enrollment)
        return {"message": "Student removed from course successfully"}

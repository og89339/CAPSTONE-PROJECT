from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repository.course_repo import CourseRepository
from app.schemas.course import CourseCreate, CourseUpdate
from typing import List


class CourseService:
    def __init__(self, db: Session):
        self.db = db
        self.course_repo = CourseRepository(db)

    def get_all_active_courses(self):
        courses = self.course_repo.get_all_active()
        result = []
        for course in courses:
            enrollment_count = self.course_repo.get_enrollment_count(course.id)
            result.append({
                **course.__dict__,
                "enrollment_count": enrollment_count,
                "available_slots": course.capacity - enrollment_count
            })
        return result

    def get_course_by_id(self, course_id: int):
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        enrollment_count = self.course_repo.get_enrollment_count(course.id)
        return {
            **course.__dict__,
            "enrollment_count": enrollment_count,
            "available_slots": course.capacity - enrollment_count
        }

    def create_course(self, course_data: CourseCreate):
        if self.course_repo.code_exists(course_data.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course code already exists"
            )

        course = self.course_repo.create(
            title=course_data.title,
            code=course_data.code,
            capacity=course_data.capacity
        )
        return course

    def update_course(self, course_id: int, course_data: CourseUpdate):
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )

        if course_data.code and course_data.code != course.code:
            if self.course_repo.code_exists(course_data.code):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Course code already exists"
                )

        update_data = course_data.model_dump(exclude_unset=True)
        updated_course = self.course_repo.update(course, **update_data)
        return updated_course

    def delete_course(self, course_id: int):
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        self.course_repo.delete(course)
        return {"message": "Course deleted successfully"}

    def toggle_course_status(self, course_id: int, is_active: bool):
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        course.is_active = is_active
        self.db.commit()
        self.db.refresh(course)
        return course

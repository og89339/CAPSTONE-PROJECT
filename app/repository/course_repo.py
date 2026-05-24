from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Course, Enrollment
from typing import Optional, List


class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, course_id: int) -> Optional[Course]:
        return self.db.query(Course).filter(Course.id == course_id).first()

    def get_by_code(self, code: str) -> Optional[Course]:
        return self.db.query(Course).filter(Course.code == code).first()

    def get_all_active(self) -> List[Course]:
        return self.db.query(Course).filter(Course.is_active == True).all()

    def get_all(self) -> List[Course]:
        return self.db.query(Course).all()

    def create(self, title: str, code: str, capacity: int) -> Course:
        db_course = Course(
            title=title,
            code=code,
            capacity=capacity,
            is_active=True
        )
        self.db.add(db_course)
        self.db.commit()
        self.db.refresh(db_course)
        return db_course

    def update(self, course: Course, **kwargs) -> Course:
        for key, value in kwargs.items():
            if value is not None:
                setattr(course, key, value)
        self.db.commit()
        self.db.refresh(course)
        return course

    def delete(self, course: Course):
        self.db.delete(course)
        self.db.commit()

    def code_exists(self, code: str) -> bool:
        return self.db.query(Course).filter(Course.code == code).first() is not None

    def get_enrollment_count(self, course_id: int) -> int:
        return self.db.query(func.count(Enrollment.id)).filter(
            Enrollment.course_id == course_id
        ).scalar()

    def is_full(self, course_id: int) -> bool:
        course = self.get_by_id(course_id)
        if not course:
            return True
        enrolled = self.get_enrollment_count(course_id)
        return enrolled >= course.capacity

from sqlalchemy.orm import Session, joinedload
from app.models import Enrollment, User, Course
from typing import List, Optional


class EnrollmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, enrollment_id: int) -> Optional[Enrollment]:
        return self.db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

    def get_by_user_and_course(self, user_id: int, course_id: int) -> Optional[Enrollment]:
        return self.db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ).first()

    def get_all(self) -> List[Enrollment]:
        return self.db.query(Enrollment).options(
            joinedload(Enrollment.user),
            joinedload(Enrollment.course)
        ).all()

    def get_by_course(self, course_id: int) -> List[Enrollment]:
        return self.db.query(Enrollment).options(
            joinedload(Enrollment.user),
            joinedload(Enrollment.course)
        ).filter(Enrollment.course_id == course_id).all()

    def get_by_user(self, user_id: int) -> List[Enrollment]:
        return self.db.query(Enrollment).options(
            joinedload(Enrollment.course)
        ).filter(Enrollment.user_id == user_id).all()

    def create(self, user_id: int, course_id: int) -> Enrollment:
        db_enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id
        )
        self.db.add(db_enrollment)
        self.db.commit()
        self.db.refresh(db_enrollment)
        return db_enrollment

    def delete(self, enrollment: Enrollment):
        self.db.delete(enrollment)
        self.db.commit()

    def is_enrolled(self, user_id: int, course_id: int) -> bool:
        return self.db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ).first() is not None

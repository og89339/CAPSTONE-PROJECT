from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse, EnrollmentWithDetails
from app.dependencies import get_current_student, get_current_admin, get_current_user
from app.services.enrollment_service import EnrollmentService
from app.models import User

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll(
    enrollment_data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_student)
):
    """Enroll the current student in a course (student only)."""
    enrollment_service = EnrollmentService(db)
    return enrollment_service.enroll_student(
        user_id=current_student.id,
        course_id=enrollment_data.course_id
    )


@router.delete("/course/{course_id}")
async def deregister(
    course_id: int,
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_student)
):
    """Deregister the current student from a course (student only)."""
    enrollment_service = EnrollmentService(db)
    return enrollment_service.deregister_student(
        user_id=current_student.id,
        course_id=course_id
    )


@router.get("/my-enrollments", response_model=List[EnrollmentWithDetails])
async def get_my_enrollments(
    db: Session = Depends(get_db),
    current_student: User = Depends(get_current_student)
):
    """Get the current student's enrollments (student only)."""
    enrollment_service = EnrollmentService(db)
    return enrollment_service.get_student_enrollments(current_student.id)


# Admin routes
@router.get("/admin/all", response_model=List[EnrollmentWithDetails])
async def get_all_enrollments(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Get all enrollments (admin only)."""
    enrollment_service = EnrollmentService(db)
    return enrollment_service.get_all_enrollments()


@router.get("/admin/course/{course_id}", response_model=List[EnrollmentWithDetails])
async def get_course_enrollments(
    course_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Get all enrollments for a specific course (admin only)."""
    enrollment_service = EnrollmentService(db)
    return enrollment_service.get_course_enrollments(course_id)


@router.delete("/admin/{enrollment_id}")
async def remove_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """Remove a student from a course (admin only)."""
    enrollment_service = EnrollmentService(db)
    return enrollment_service.remove_student_from_course(enrollment_id)

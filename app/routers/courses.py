from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse, CourseWithEnrollmentCount
from app.dependencies import get_current_admin
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/", response_model=List[CourseWithEnrollmentCount])
async def list_courses(db: Session = Depends(get_db)):
    """List all active courses (public access)."""
    course_service = CourseService(db)
    return course_service.get_all_active_courses()


@router.get("/{course_id}", response_model=CourseWithEnrollmentCount)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get a course by ID (public access)."""
    course_service = CourseService(db)
    return course_service.get_course_by_id(course_id)


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """Create a new course (admin only)."""
    course_service = CourseService(db)
    return course_service.create_course(course_data)


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """Update a course (admin only)."""
    course_service = CourseService(db)
    return course_service.update_course(course_id, course_data)


@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """Delete a course (admin only)."""
    course_service = CourseService(db)
    return course_service.delete_course(course_id)


@router.patch("/{course_id}/activate")
async def activate_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """Activate a course (admin only)."""
    course_service = CourseService(db)
    return course_service.toggle_course_status(course_id, True)


@router.patch("/{course_id}/deactivate")
async def deactivate_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    """Deactivate a course (admin only)."""
    course_service = CourseService(db)
    return course_service.toggle_course_status(course_id, False)

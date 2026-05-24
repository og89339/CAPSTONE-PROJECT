from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class EnrollmentCreate(BaseModel):
    course_id: int


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserInfo(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class CourseInfo(BaseModel):
    id: int
    title: str
    code: str

    model_config = ConfigDict(from_attributes=True)


class EnrollmentWithDetails(BaseModel):
    id: int
    user: UserInfo
    course: CourseInfo
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

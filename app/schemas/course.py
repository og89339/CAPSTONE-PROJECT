from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from typing import Optional


class CourseBase(BaseModel):
    title: str
    code: str
    capacity: int


class CourseCreate(CourseBase):

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title is required")
        if len(v) > 200:
            raise ValueError("Title must not exceed 200 characters")
        return v.strip()

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError("Code is required")
        if len(v) > 50:
            raise ValueError("Code must not exceed 50 characters")
        return v.strip().upper()

    @field_validator("capacity")
    @classmethod
    def validate_capacity(cls, v):
        if v <= 0:
            raise ValueError("Capacity must be greater than zero")
        return v


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Title cannot be empty")
            if len(v) > 200:
                raise ValueError("Title must not exceed 200 characters")
        return v

    @field_validator("code")
    @classmethod
    def validate_code(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Code cannot be empty")
            if len(v) > 50:
                raise ValueError("Code must not exceed 50 characters")
        return v.strip().upper() if v else v

    @field_validator("capacity")
    @classmethod
    def validate_capacity(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Capacity must be greater than zero")
        return v


class CourseResponse(BaseModel):
    id: int
    title: str
    code: str
    capacity: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CourseWithEnrollmentCount(CourseResponse):
    enrollment_count: int = 0
    available_slots: int = 0

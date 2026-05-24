from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (student or admin)."""
    auth_service = AuthService(db)
    user = auth_service.register_user(
        name=user_data.name,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role
    )
    return user


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Log in a user and return a JWT token."""
    auth_service = AuthService(db)
    token = auth_service.authenticate_user(
        email=login_data.email,
        password=login_data.password
    )
    return token

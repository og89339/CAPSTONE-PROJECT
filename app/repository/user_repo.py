from sqlalchemy.orm import Session
from app.models import User
from app.utils.security import hash_password
from typing import Optional, List


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_all(self) -> List[User]:
        return self.db.query(User).all()

    def create(self, name: str, email: str, password: str, role: str = "student") -> User:
        db_user = User(
            name=name,
            email=email,
            hashed_password=hash_password(password),
            role=role,
            is_active=True
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def email_exists(self, email: str) -> bool:
        return self.db.query(User).filter(User.email == email).first() is not None

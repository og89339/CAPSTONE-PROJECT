import os
from functools import lru_cache


class Settings:
    def __init__(self):
        self.app_name: str = "Course Enrollment Platform API"
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./course_enrollment.db")
        self.secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm: str = "HS256"
        self.access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


@lru_cache()
def get_settings():
    return Settings()

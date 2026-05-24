from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, users, courses, enrollments
from app.config import get_settings

settings = get_settings()

# Create all tables (for development; use Alembic for production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="A secure RESTful API for managing course enrollments",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(courses.router, prefix="/api")
app.include_router(enrollments.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Welcome to Course Enrollment Platform API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

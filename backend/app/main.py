from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.db.database import init_db, get_db
from app.api.v1.endpoints import router as api_v1_router
from app.api.v1.elevenlabs_routes import router as elevenlabs_router
from app.api.v1.google_auth_routes import router as google_auth_router, legacy_router as google_legacy_router
from app.api.v1.meeting_routes import router as meeting_router
from app.api.v1.coding_routes import router as coding_router
from app.api.v1.evaluation_routes import ai_router as evaluation_ai_router, hr_router as evaluation_hr_router
from app.api.v1.workflow_routes import workflow_router, candidate_wf_router

# Initialize database tables
init_db()

app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    description="Enterprise Multi-Tenant AI HR Agent Hiring Platform Backend API (Single Source of Truth PostgreSQL Engine)"
)

# Configure CORS Middleware using centralized settings
origins = settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if settings.APP_ENV == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(api_v1_router)
app.include_router(elevenlabs_router)
app.include_router(google_auth_router)
app.include_router(google_legacy_router)
app.include_router(meeting_router)
app.include_router(coding_router)
app.include_router(evaluation_ai_router)
app.include_router(evaluation_hr_router)
app.include_router(workflow_router)
app.include_router(candidate_wf_router)

@app.get("/")
@app.get("/health")
def read_root():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health/database")
def check_database_health(db: Session = Depends(get_db)):
    """Verifies single source of truth database connection health."""
    try:
        db.execute(text("SELECT 1"))
        db_type = "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite"
        return {
            "status": "ok",
            "database": "connected",
            "type": db_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database health check failed: {str(e)}")

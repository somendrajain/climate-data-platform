from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Perform a direct query to PostgreSQL to verify connectivity
        result = db.execute(text("SELECT 1 as is_alive")).fetchone()

        db_alive = result[0] == 1 if result else False
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(exc)}",
        )

    return {
        "status": "ok",
        "database": "connected" if db_alive else "disconnected",
        "service": "FastAPI Climate Data Platform API",
    }

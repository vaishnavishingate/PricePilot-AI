from datetime import datetime
from fastapi import APIRouter

router = APIRouter(tags=["system"])

@router.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "3.0.0"}

@router.get("/ready")
def readiness_check():
    return {"status": "ready", "timestamp": datetime.now().isoformat()}

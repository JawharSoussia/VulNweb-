"""Health Check Routes"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def status():
    """API status endpoint"""
    return {"status": "operational"}
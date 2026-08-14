from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings

router = APIRouter(
    prefix="/users",    
    tags=["users"],
)



@router.get("/me")
async def session_verify():
   return {}
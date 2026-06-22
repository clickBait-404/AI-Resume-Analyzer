"""
Auth routes: register, login, current user.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user
from database.session import get_db
from models.user import User
from schemas.auth import TokenResponse, UserLogin, UserOut, UserRegister
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    service = AuthService(db)
    result = service.register(payload)
    return result


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    service = AuthService(db)
    result = service.login(payload)
    return result


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns the currently authenticated user. Used by the frontend to
    validate a stored token is still good on app load, without
    requiring a full re-login.
    """
    return current_user

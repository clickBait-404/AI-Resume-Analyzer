"""
Auth service: registration and login business logic.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import create_access_token, hash_password, verify_password
from repositories.user_repository import UserRepository
from schemas.auth import UserLogin, UserRegister


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, payload: UserRegister) -> dict:
        existing = self.user_repo.get_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")

        user = self.user_repo.create(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
        )
        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token, "user": user}

    def login(self, payload: UserLogin) -> dict:
        user = self.user_repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")

        token = create_access_token({"sub": str(user.id)})
        return {"access_token": token, "user": user}

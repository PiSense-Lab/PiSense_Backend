from datetime import timedelta

from fastapi import APIRouter, HTTPException
from pisense.backend.classes import Authenticator, User
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import JWTError, jwt

router = APIRouter(prefix="/users")

@router.get("/verify-token/{token}")
async def verify_user_token(token: str):
    Authenticator().verify_token(token==token)
    return {"message": "Token is valid"}

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = Authenticator().authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token= Authenticator().create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=Authenticator.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

from datetime import timedelta

from fastapi import APIRouter, HTTPException
from pisense.backend.classes import Authenticator, User
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import JWTError, jwt

from pisense.backend.exceptions import DatabaseError

router = APIRouter(prefix="/users")

@router.get("/verify-token")
async def verify_user_token(payload=Depends(Authenticator().verify_token)):
    return {"message": "Token is valid", "payload": payload}

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = Authenticator().authenticate_user(form_data.username, form_data.password)
    except DatabaseError:
        user = None
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token= Authenticator().create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=int(Authenticator().ACCESS_TOKEN_EXPIRE_MINUTES)))
    return {"access_token": access_token, "token_type": "bearer"}

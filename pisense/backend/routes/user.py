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

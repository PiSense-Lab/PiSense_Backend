from datetime import timedelta

from pisense.backend.classes import Database

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pisense.backend.classes import Authenticator, Database

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from pisense.backend.exceptions import DatabaseError

router = APIRouter(prefix="/users")

@router.get("/verify-token")
async def verify_user_token(payload=Depends(Authenticator().verify_token)):
    return {"message": "Token is valid", "payload": payload}

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), extended: bool | None = None, ):
    try:
        user = Authenticator().authenticate_user(form_data.username, form_data.password)
    except DatabaseError as e:
        print(f"DB Error, Skipping - {e}")
        user = None
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expire: timedelta | None = None
    if extended:
        expire = timedelta(days=int(Authenticator().PISENSE_AUTH_ACCESS_TOKEN_REMEMBER_ME_DAYS))

    access_token= Authenticator().create_access_token(data={"sub": user.username, "id": user.id}, expires_delta=expire)
    return {"access_token": access_token, "token_type": "bearer"}

class Create_User_Input(BaseModel):
    username: str
    email: str
    password: str
    firstname: str | None = None
    lastname: str | None = None

@router.post("/create_user", status_code=201)
async def create_user(
    user_values: Create_User_Input
):
    """
    Create a new user.

    params:
        user_values: Request Body for Creating a user

    returns:
        The created user record.
    """
    db = Database()
    user = db.create_user(
        username=user_values.username,
        email=user_values.email,
        password=user_values.password,
        firstname=user_values.firstname,
        lastname=user_values.lastname,
    )
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "firstname": user.firstname,
        "lastname": user.lastname,
    }

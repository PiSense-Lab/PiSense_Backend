from datetime import timedelta

from pisense.backend.classes import Database

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pisense.backend.classes import Authenticator

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from pisense.backend.exceptions import DatabaseError, DatabaseReconnectingError

router = APIRouter(prefix="/users")

@router.get("/verify-token")
async def verify_user_token(payload=Depends(Authenticator().verify_token)):
    return {"message": "Token is valid", "payload": payload}

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), extended: bool | None = None, ):
    try:
        user = Authenticator().authenticate_user(form_data.username, form_data.password)
    except DatabaseError as e:
        print(f"{e}")
        user = None
    except DatabaseReconnectingError as e:
        print(f"{e}")
        raise HTTPException(
            status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS,
            detail="Database Is Reconnecting, Try Again",
            headers={"WWW-Authenticate": "Bearer"},
        )
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

@router.get("")
async def get_all_users():
    """
    Gets all users in the database.

    Returns:
        (int): id 
        (int): role users role (ask for nums?)
        (str): username users shown name
        (str): email 
        (str): firstname 
        (str): lastname 
        (str): hashed_password

    """
    db = Database()
    return db.get_users()

async def get_users(username: str | None = None):
    """
    Retrieve user records.

    params:
        username: Optional username to filter results.

    returns:
        (List): List of user objects or matching user records.
    """
    db = Database()
    return db.get_users(username=username)


@router.get("/get_user_projects")
async def get_user_projects(user_id: int | None = None):
    """
    Retrieve projects associated with a user.

    params:
        user_id: Optional user ID to filter projects.

    returns:
        (dict): data - A dictionary containing project records for the user.
    """
    db = Database()
    res = db.get_projects_for_user(user_id)
    return {"data": res}

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
        (int): id
        (str): username
        (str): email
        (str): firstname
        (str): lastname
    """
    db = Database()
    try:
        user = db.create_user(
            username=user_values.username,
            email=user_values.email,
            password=user_values.password,
            firstname=user_values.firstname,
            lastname=user_values.lastname,
        )
    except DatabaseError as e:
        if "unique_username" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Username is not unique",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif "unique_email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email is not unique",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unhandled Exception: {e}",
                headers={"WWW-Authenticate": "Bearer"},
            )


    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "firstname": user.firstname,
        "lastname": user.lastname,
    }

from datetime import timedelta

<<<<<<< HEAD
from pisense.backend.classes import Database
=======
<<<<<<< HEAD
from pisense.backend.classes import USER_ROLES, Database
=======
from pisense.backend.classes import Database
>>>>>>> bf93cde095efaed7601eb314c42aaf6e9fb51891
>>>>>>> main

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pisense.backend.classes import Authenticator

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

<<<<<<< HEAD
=======
<<<<<<< HEAD
@router.get("/get_users")
=======
>>>>>>> main
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

<<<<<<< HEAD
=======
>>>>>>> bf93cde095efaed7601eb314c42aaf6e9fb51891
>>>>>>> main
async def get_users(username: str | None = None):
    """
    Retrieve user records.

    params:
        username: Optional username to filter results.

    returns:
<<<<<<< HEAD
        (List): List of user objects or matching user records.
=======
<<<<<<< HEAD
        List of user objects or matching user records.
=======
        (List): List of user objects or matching user records.
>>>>>>> bf93cde095efaed7601eb314c42aaf6e9fb51891
>>>>>>> main
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
<<<<<<< HEAD
        (dict): data - A dictionary containing project records for the user.
=======
<<<<<<< HEAD
        A dictionary containing project records for the user.
=======
        (dict): data - A dictionary containing project records for the user.
>>>>>>> bf93cde095efaed7601eb314c42aaf6e9fb51891
>>>>>>> main
    """
    db = Database()
    res = db.get_projects_for_user(user_id)
    return {"data": res}

<<<<<<< HEAD

@router.post("/create_user", status_code=201)
async def create_user(
    username: str,
    email: str,
    password: str,
    firstname: str | None = None,
    lastname: str | None = None,
=======
class Create_User_Input(BaseModel):
    username: str
    email: str
    password: str
    firstname: str | None = None
    lastname: str | None = None

@router.post("/create_user", status_code=201)
async def create_user(
    user_values: Create_User_Input
>>>>>>> bf93cde095efaed7601eb314c42aaf6e9fb51891
):
    """
    Create a new user.

    params:
<<<<<<< HEAD
        username: Username for the new user.
        email: Email address.
        password: Password in plaintext.
        firstname: Optional first name.
        lastname: Optional last name.
=======
        user_values: Request Body for Creating a user
>>>>>>> bf93cde095efaed7601eb314c42aaf6e9fb51891

    returns:
        (int): id
        (str): username
        (str): email
        (str): firstname
        (str): lastname
    """
    db = Database()
    user = db.create_user(
<<<<<<< HEAD
        username=username,
        email=email,
        password=password,
        firstname=firstname,
        lastname=lastname,
=======
        username=user_values.username,
        email=user_values.email,
        password=user_values.password,
        firstname=user_values.firstname,
        lastname=user_values.lastname,
>>>>>>> bf93cde095efaed7601eb314c42aaf6e9fb51891
    )
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "firstname": user.firstname,
        "lastname": user.lastname,
    }
<<<<<<< HEAD

=======
>>>>>>> bf93cde095efaed7601eb314c42aaf6e9fb51891

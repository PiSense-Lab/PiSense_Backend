# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
from pisense.api.main import Database

def test_get_datasets():
    with TestClient(app): # Will run with lifecycle function
        db = Database()
        datasets = db._get_rows("dataset") # noqa: F841


# CREATE TABLE dataset (
#     dataset_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
#     project_id INT DEFAULT NULL,
#     tablename VARCHAR(50) DEFAULT NULL
# );

def test_get_projects_table():
    with TestClient(app): # Will run with lifecycle function
        db = Database()
        projects = db._get_rows("projects") # noqa: F841

# CREATE TABLE projects (
#     project_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
#     project_name VARCHAR(100) NOT NULL,
#     description TEXT DEFAULT NULL,
#     public TINYINT(1) DEFAULT NULL,
#     archived TINYINT(1) DEFAULT NULL
# );

def test_get_roles_table():
    with TestClient(app): # Will run with lifecycle function
        db = Database()
        roles = db._get_rows("roles") # noqa: F841

# CREATE TABLE roles (
#     role_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
#     name VARCHAR(50) DEFAULT NULL,
#     permissions ENUM('Analyst', 'Viewer', 'Admin') DEFAULT NULL
# );

def test_get_user_projects_table():
    with TestClient(app): # Will run with lifecycle function
        db = Database()
        user_projects = db._get_rows("user_projects") # noqa: F841


# CREATE TABLE user_projects (
#     user_projects_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
#     user_id INT DEFAULT NULL,
#     project_id INT DEFAULT NULL,
#     role_id INT DEFAULT NULL
# )

def test_get_users_table():
    with TestClient(app): # Will run with lifecycle function
        db = Database()
        users = db._get_rows("users") # noqa: F841

# CREATE TABLE users (
#     id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
#     role ENUM('admin', 'analyst', 'viewer')
#     username VARCHAR(50) UNIQUE DEFAULT NULL,
#     email VARCHAR(100) DEFAULT NULL,
#     password VARCHAR(255) UNIQUE DEFAULT NULL,
#     firstname VARCHAR(50) DEFAULT NULL,
#     lastname VARCHAR(50) DEFAULT NULL
# )

-- init.sql
-- This script runs on database startup

CREATE DATABASE IF NOT EXISTS PiSense;
USE PiSense;

CREATE TABLE dataset (
    dataset_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    project_id INT DEFAULT NULL,
    tablename VARCHAR(50) DEFAULT NULL
);

CREATE TABLE projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    project_name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT NULL,
    public TINYINT(1) DEFAULT NULL,
    archived TINYINT(1) DEFAULT NULL
);

CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    name VARCHAR(50) DEFAULT NULL,
    permissions ENUM('Analyst', 'Viewer', 'Admin') DEFAULT NULL
);

CREATE TABLE user_projects (
    user_projects_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    user_id INT DEFAULT NULL,
    project_id INT DEFAULT NULL,
    role_id INT DEFAULT NULL
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    role ENUM('admin', 'analyst', 'viewer'),
    username VARCHAR(50) UNIQUE DEFAULT NULL,
    email VARCHAR(100) DEFAULT NULL,
    password VARCHAR(255) UNIQUE DEFAULT NULL,
    firstname VARCHAR(50) DEFAULT NULL,
    lastname VARCHAR(50) DEFAULT NULL
);



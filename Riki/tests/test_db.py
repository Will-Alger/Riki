from Riki import app
import os
import tempfile
import unittest
import sqlite3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pytest
from wiki.web.userDAO import UserDao, UserDaoManager
from wiki.web.db import *
from datetime import datetime


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config["DATABASE"] = db_path
    app.config["TESTING"] = True
    app.config[
        "PRIVATE"
    ] = False  # sets PRIVATE to false to disable user auth (see protect dectorator in users.py)
    app.config[
        "WTF_CSRF_ENABLED"
    ] = False  # disables CSRF in WTForms so that we can simulate posts
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def user_dao_manager(client):
    with app.app_context():
        db_path = app.config["DATABASE"]
        dao_manager = UserDaoManager(db_path)
        yield dao_manager
        dao_manager.close_db()


def test_db_file_created(client):
    db_path = app.config["DATABASE"]
    assert os.path.exists(db_path), "Database file not created"


def test_users_table_created(client):
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute("PRAGMA table_info('users')")
        table_info = cur.fetchall()
    assert table_info, "users table not created or empty"


def test_create_user(user_dao_manager):
    signup_time = datetime.utcnow()
    user = UserDao("John", "Doe", "john@example.com", "password123", signup_time)
    user_dao_manager.create_user(user)
    result = user_dao_manager.get_user(user.email)
    assert result.email == user.email
    assert result.signup_time == signup_time


def test_get_users(user_dao_manager):
    signup_time = datetime.utcnow()
    user1 = UserDao("John", "Doe", "john@example.com", "passwordJohnDoe", signup_time)
    user2 = UserDao("Jane", "Smith", "jane@example.com", "passwordJaneSmith", signup_time)
    user_dao_manager.create_user(user1)
    user_dao_manager.create_user(user2)
    result = user_dao_manager.get_users()
    assert len(result) == 2
    print(f" Tedyooo -> {result[0]}")
    assert result[0][1] == user1.first_name
    assert result[0][2] == user1.last_name
    assert result[0][3] == user1.email
    assert result[1][3] == user2.email
    assert result[0][5] == signup_time


def test_get_user(user_dao_manager):
    signup_time = datetime.utcnow()
    user = UserDao("John", "Doe", "john@example.com", "password123", signup_time)
    user_dao_manager.create_user(user)
    result = user_dao_manager.get_user(user.email)
    assert result.first_name == user.first_name
    assert result.last_name == user.last_name
    assert result.email == user.email
    assert result.signup_time == signup_time

def test_delete_all_users(user_dao_manager):
    signup_time = datetime.utcnow()
    user1 = UserDao("John", "Doe", "john@example.com", "passwordJohnDoe", signup_time)
    user2 = UserDao("Jane", "Smith", "jane@example.com", "passwordJaneSmith", signup_time)
    user_dao_manager.create_user(user1)
    user_dao_manager.create_user(user2)

    result = user_dao_manager.get_users()
    assert len(result) == 2

    user_dao_manager.delete_all_users()
    result = user_dao_manager.get_users()
    assert len(result) == 0

def test_delete_existing_user(user_dao_manager):
    user = UserDao("John", "Doe", "john@example.com", "password123", datetime.utcnow())
    user_dao_manager.create_user(user)
    result = user_dao_manager.get_user(user.email)
    assert result.email == user.email

    result = user_dao_manager.delete_user(user.email)
    assert result == True

    all_users = user_dao_manager.get_users()
    assert len(all_users) == 0

def test_delete_nonexistent_user(user_dao_manager):
    nonexistent_email = "emaildne@riki.com"
    result = user_dao_manager.delete_user(nonexistent_email)
    assert result == False

    all_users = user_dao_manager.get_users()
    assert len(all_users) == 0

def test_record_history(client, user_dao_manager):
    url = 'ORIGINS'
    user = UserDao("John", "Doe", "john@example.com", "password123", datetime.utcnow())
    user_dao_manager.create_user(user)
    result = user_dao_manager.get_user(user.email)

    # make an edit to a page
    client.post(
        "/edit/ORIGINS",
        headers={"Content-Type": "multipart/form-data"},
        data={
            "title": "ORIGINS FROM EVERYWHERE",
            "body": "i edited the testpage",
            "tags": "test, edited",
        },
        follow_redirects=True,
    )

    edits = user_dao_manager.record_history(result.email, url, datetime.now())

    print(f"Teddyoo -> {edits}")
    assert 1 == 2

def test_record_history_returns_none(user_dao_manager):
    url = 'ORIGINS'
    user = UserDao("John", "Doe", "john@example.com", "password123", datetime.utcnow())

    edits = user_dao_manager.record_history(user.email, url, datetime.now())

    assert edits == None
    

def test_get_edit_history(user_dao_manager):
    pass

def test_close_db(user_dao_manager):
    assert user_dao_manager.close_db() is None, "Database connection not closed"


def test_UserDao_constructor(user_dao_manager):
    first_name = "John"
    last_name = "Doe"
    email = "john@example.com"
    password = "password123"
    user = UserDao(first_name, last_name, email, password, datetime.utcnow())

    assert user.first_name == first_name
    assert user.last_name == last_name
    assert user.email == email
    assert user.password == password

    assert not user.is_authenticated()
    assert user.is_active()
    assert not user.is_anonymous()
    assert isinstance(user.get_id(), str)

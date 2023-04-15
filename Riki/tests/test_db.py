from Riki import app
import wiki.web.init_db
from wiki.web.init_db import init_db
import os
import tempfile
import unittest
import sqlite3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pytest
from wiki.web.userDAO import UserDao, UserDaoManager
from wiki.web.db import *

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config['DATABASE'] = db_path
    app.config['TESTING'] = True
    app.config["PRIVATE"] = False #sets PRIVATE to false to disable user auth (see protect dectorator in users.py)
    app.config["WTF_CSRF_ENABLED"] = False #disables CSRF in WTForms so that we can simulate posts
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def user_dao_manager(client):
    db_path = app.config['DATABASE']
    dao_manager = UserDaoManager(db_path)
    yield dao_manager
    dao_manager.close_db()

def test_db_file_created(client):
    db_path = app.config['DATABASE']
    assert os.path.exists(db_path), "Database file not created"

def test_users_table_created(client):
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute("PRAGMA table_info('users')")
        table_info = cur.fetchall()
    assert table_info, "users table not created or empty"
 
def test_create_user(user_dao_manager):
    user = UserDao('John Doe', 'john@example.com', 'password123')
    user_dao_manager.create_user(user)
    result = user_dao_manager.get_user(user.email)
    assert result[0] == user.email

def test_get_users(user_dao_manager):
    user1 = UserDao('John Doe', 'john@example.com', 'passwordJohnDoe')
    user2 = UserDao('Jane Smith', 'jane@example.com', 'passwordJaneSmith')
    user_dao_manager.create_user(user1)
    user_dao_manager.create_user(user2)
    result = user_dao_manager.get_users()
    assert len(result) == 2
    assert result[0]['name'], user1.name
    assert result[1]['email'], user2.email

def test_get_user(user_dao_manager):
    user = UserDao('John Doe', 'john@example.com', 'password123')
    user_dao_manager.create_user(user)
    result = user_dao_manager.get_user(user.email)
    assert result[0] == user.email

def test_close_db(user_dao_manager):
    assert user_dao_manager.close_db() is None, "Database connection not closed"

def test_UserDao_constructor():
    name = 'John Doe'
    email = 'john@example.com'
    password = 'password123'
    user = UserDao(name, email, password)
    
    assert user.name == name
    assert user.email == email
    assert user.password == password
    
    assert not user.is_authenticated()
    assert user.is_active()
    assert not user.is_anonymous()
    assert isinstance(user.get_id(), str)

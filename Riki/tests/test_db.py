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

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config["PRIVATE"] = False #sets PRIVATE to false to disable user auth (see protect dectorator in users.py)
    app.config["WTF_CSRF_ENABLED"] = False #disables CSRF in WTForms so that we can simulate posts

    init_db(db_path, force=True)
    with app.test_client() as client:
        client.db_path = db_path # Add the database path as an attribute of the client
        with app.app_context():
            pass #if we need stuff in app context we can do it here
        yield client
    os.close(db_fd)
    os.unlink(db_path)

def test_db_file_created(client):
    db_path = client.db_path
    assert os.path.exists(db_path), "Database file not created"

def test_users_table_created(client):
    db_path = client.db_path
    with sqlite3.connect(db_path) as connection:
        cur = connection.cursor()
        cur.execute("PRAGMA table_info('users')")
        table_info = cur.fetchall()
        print("Query result:", table_info)
    assert table_info, "users table not created or empty"
import pytest
from Riki import app
from app import db
import sqlite3


@pytest.fixture
def client():
    app.config["TESTING"] = True #sets testing to true, needed for Flask to return proper response
    app.config["PRIVATE"] = False #sets PRIVATE to false to disable user auth (see protect dectorator in users.py)
    app.config["WTF_CSRF_ENABLED"] = False #disables CSRF in WTForms so that we can simulate posts
    with app.test_client() as client:
        with app.app_context():
            pass #if we need stuff in app context we can do it here
        yield client


class TestDB:
    def test_db_post_model(app):
        

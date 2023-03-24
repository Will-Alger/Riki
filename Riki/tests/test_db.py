
import pytest
from Riki import app

import os
import tempfile
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class TestInitDB(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = app.test_client()
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        app.config['TESTING'] = True
        init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_db_file_created(self):
        assert os.path.exists(self.db_path), "Database file not created"

# @pytest.fixture
# def client(self):
#     self.db_uri = 'sqlite:///' + os.path.join(basedir, 'test.db')
#     app.config["TESTING"] = True #sets testing to true, needed for Flask to return proper response
#     app.config["PRIVATE"] = False #sets PRIVATE to false to disable user auth (see protect dectorator in users.py)
#     app.config["WTF_CSRF_ENABLED"] = False #disables CSRF in WTForms so that we can simulate posts
#     with app.test_client() as client:
#         with app.app_context():
#             pass #if we need stuff in app context we can do it here
            
#         yield client
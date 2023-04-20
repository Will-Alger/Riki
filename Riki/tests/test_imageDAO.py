from Riki import app

import os
import tempfile
import pytest
from wiki.web.imageDAO import ImageDAO
from wiki.web.db import *

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
def dao():
    with app.app_context():
        thing = ImageDAO()
    yield thing

def test_filename_exists(client, dao):
    assert not dao.filename_exists('filename.jpg')
    dao.save_image('filename.jpg', 'email@email.com')
    assert dao.filename_exists('filename.jpg')

def test_save_image(client, dao):
    dao.save_image('filename.jpg', 'email@email.com')
    assert dao.filename_exists('filename.jpg')

def test_get_user_images(client, dao):
    dao.save_image('filename.jpg', 'email@email.com')
    dao.save_image('filename2.jpg', 'email2@email.com')
    dao.save_image('filename3.jpg', 'email2@email.com')
    dao.save_image('filename4.jpg', 'email@email.com')
    dao.save_image('filename5.jpg', 'email@email.com')

    ret = dao.get_user_images("email@email.com")
    ret2 = dao.get_user_images('email2@email.com')

    assert len(ret) == 3
    assert len(ret2) == 2




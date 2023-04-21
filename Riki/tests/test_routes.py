import pytest
from unittest.mock import patch
import os
from io import BytesIO
from Riki import app
from PIL import Image
import wiki.web.routes
import tempfile
import config
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


# this fixture will create a page that we can test on, and destroy it when our
# test is over.  Check out the official pytest docs for more details on fixtures.
@pytest.fixture
def testpage():
    with open("content/testpage.md", "w") as testpage:  # open a fresh file
        testpage.write(
            "title: testpage\ntags: test dummy\n\nThis is a test page."
        )  # write contents
        testpage.flush()  # flush buffer so contents are actually written to file
        yield testpage  # yield the fixutre
        os.unlink(
            "content/testpage.md"
        )  # after our test is over, this code executes to delete the file.  anything after yeild in a fixture is cleanup


def test_home(client):
    rv = client.get("/", follow_redirects=True)
    assert b"Main" in rv.data

    # here we stub wiki.web.routes.current_wiki to a MagicMock (see official docs about MagicMock, its built into python.
    # note how we use the full module name to patch the source of the object.
    # if we just did patch('current_wiki') that would only patch the reference in this file
    with patch("wiki.web.routes.current_wiki") as mock_current_wiki:
        mock_current_wiki.get.return_value = None
        rv = client.get("/", follow_redirects=True)
        assert (
            b"You did not create any content yet. Your wiki recommends you, to do so now, as every user will see this page first, and you would want to make a good impression, wouldn't you?"
            in rv.data
        )


def test_index(client):
    rv = client.get("/index/", follow_redirects=True)
    assert b"Page Index" in rv.data


def test_display_404(client):
    rv = client.get("/foo/", follow_redirects=True)
    assert rv.status_code == 404


def test_create_get(client):
    rv = client.get("/create/", follow_redirects=True)
    assert b"Create a new page" in rv.data


def test_create_post(client):
    # example of posting a form, in this case we get redirected
    rv = client.post(
        "/create/", headers={"Content-Type": "multipart/form-data"}, data={"url": "bar"}
    )
    assert (
        b'You should be redirected automatically to target URL: <a href="/edit/bar/">/edit/bar/</a>'
        in rv.data
    )


# def test_create_post_existing_page(client):
#     #example of posting a form when it already exists, in this case we get redirected
#     client.post("/create/", 
#         headers={"Content-Type":"multipart/form-data"}, 
#         data={"url":"existing_page"}
#     )

#     rv = client.post("/create/", 
#         headers={"Content-Type":"multipart/form-data"}, 
#         data={"url":"existing_page"}
#     )

#     asd =rv.data.decode('utf-8')
#     print(f'Teddy -> {asd}')

#     assert b'Create a new page' in rv.data

def test_edit_post(client, testpage):
    # another example of posting a form
    rv = client.post(
        "/edit/testpage",
        headers={"Content-Type": "multipart/form-data"},
        data={
            "title": "testpage",
            "body": "i edited the testpage",
            "tags": "test, edited",
        },
        follow_redirects=True,
    )
    
    
    assert b'&#34;testpage&#34; was saved.' in rv.data
    #this is to read the file and see if it was actually edited
    with open("content/testpage.md", "r") as filein:
        assert "i edited the testpage" in filein.read()

def test_user_login_successful(client):
    user_data = {
        'first_name': 'john',
        'last_name':  'doe',
        'email': 'johnDoe@riki.com',
        'password': 'password',
        'confirm_password': 'password',
    }
    client.post(
        '/user/create/',
        data=user_data,
        follow_redirects=True
    )

    rv = client.post('/user/login/', data=dict(
        email='johnDoe@riki.com',
        password='password'
    ), follow_redirects=True)

    assert b'Login successful.' in rv.data

def test_user_login_unsuccessful(client):
    user_data = {
        'first_name': 'john',
        'last_name':  'doe',
        'email': 'johnDoe@riki.com',
        'password': 'password',
        'confirm_password': 'password',
    }
    client.post(
        '/user/create/',
        data=user_data,
        follow_redirects=True
    )

    rv = client.post('/user/login/', data=dict(
        email='johnDoe@riki.com',
        password='passwordInCorrect'
    ), follow_redirects=True)
    
    assert b'Errors occured verifying your input. Please check the marked fields below.' in rv.data

def test_user_create_successful(client):
    user_data = {
        'first_name': 'john',
        'last_name':  'doe',
        'email': 'johnDoe@riki.com',
        'password': 'password',
        'confirm_password': 'password',
    }
    rv = client.post(
        '/user/create/',
        data=user_data,
        follow_redirects=True
    )

    # import pdb; pdb.set_trace()
    assert b'Sign up successful.' in rv.data

def test_user_create_unsuccessful(client):
    user_data = {
        'first_name': 'john',
        'last_name':  'doe',
        'email': 'johnDoe@riki.com',
        'password': 'password',
        'confirm_password': 'passwordNotConfirming',
    }
    rv = client.post(
        '/user/create/',
        data=user_data,
        follow_redirects=True
    )

    # import pdb; pdb.set_trace()
    assert b'Errors occured verifying your input. Please check the marked fields below.' in rv.data

def test_user_logout(client):
    user_data = {
        'first_name': 'john',
        'last_name':  'doe',
        'email': 'johnDoe@riki.com',
        'password': 'password',
        'confirm_password': 'password',
    }
    client.post(
        '/user/create/',
        data=user_data,
        follow_redirects=True
    )

    rv = client.get(
        '/user/logout/',
        follow_redirects=True
    )

    # import pdb; pdb.set_trace()
    assert b'Logout successful.' in rv.data


def test_user_profile(client):

    user_data = {
        'first_name': 'john',
        'last_name':  'doe',
        'email': 'johnDoe@riki.com',
        'password': 'password',
        'confirm_password': 'password',
    }
    client.post(
        '/user/create/',
        data=user_data,
        follow_redirects=True
    )
    
    client.post('/user/login/', data=dict(
        email='johnDoe@riki.com',
        password='password'
    ), follow_redirects=True)
    
    rv = client.get('/user/profile/', follow_redirects=True)
    # print(rv.data.decode('utf-8'))
    assert b'Profile' in rv.data
    assert b'Welcome, John' in rv.data


def test_upload_image(client):
    # login necessary
    user_data = {
        'first_name': 'john',
        'last_name':  'doe',
        'email': 'johnDoe@riki.com',
        'password': 'password',
        'confirm_password': 'password',
    }
    rv2 = client.post(
        '/user/create/',
        data=user_data,
        follow_redirects=True
    )
    
    rv1 = client.post('/user/login/', data=dict(
        email='johnDoe@riki.com',
        password='password'
    ), follow_redirects=True)

    file = tempfile.NamedTemporaryFile(suffix='.jpg')
    file.filename = 'filename.jpg'
    # send the request
    rv = client.post(
        "/user/upload/",
        data={"an_image": file},
        follow_redirects=True,
    )

    # big win
    assert b'Image Saved' in rv.data
    assert os.path.exists(os.path.join(config.PIC_BASE, file.filename))

def test_upload_image_error(client):
    # login necessary
    user_data = {
        'first_name': 'john',
        'last_name':  'doe',
        'email': 'johnDoe@riki.com',
        'password': 'password',
        'confirm_password': 'password',
    }
    client.post(
        '/user/create/',
        data=user_data,
        follow_redirects=True
    )
    
    client.post('/user/login/', data=dict(
        email='johnDoe@riki.com',
        password='password'
    ), follow_redirects=True)

    # send the request
    rv = client.post(
        "/user/upload",
        headers={"Content-Type": "multipart/form-data"},
        data={"an_image": (tempfile.TemporaryFile(), 'filename.bad')},
        follow_redirects=True,
    )

    # big win
    assert b"File name not allowed!" in rv.data


def test_upload_image_no_file_error(client):
    # login necessary
    user_data = {
        'first_name': 'john',
        'last_name':  'doe',
        'email': 'johnDoe@riki.com',
        'password': 'password',
        'confirm_password': 'password',
    }
    client.post(
        '/user/create/',
        data=user_data,
        follow_redirects=True
    )
    
    client.post('/user/login/', data=dict(
        email='johnDoe@riki.com',
        password='password'
    ), follow_redirects=True)

    # send the request
    rv = client.post(
        "/user/upload",
        headers={"Content-Type": "multipart/form-data"},
        # should not accept none type
        data={"an_image": None},
        follow_redirects=True,
    )

    assert b"There is no image!" in rv.data

def test_upload_image_repeat_filename_error(client):
    user_data = {
        'first_name': 'john',
        'last_name':  'doe',
        'email': 'johnDoe@riki.com',
        'password': 'password',
        'confirm_password': 'password',
    }
    client.post(
        '/user/create/',
        data=user_data,
        follow_redirects=True
    )
    
    client.post('/user/login/', data=dict(
        email='johnDoe@riki.com',
        password='password'
    ), follow_redirects=True)


    rv1 = client.post(
        "/user/upload/",
        headers={'content-type':'multipart/form-data'},
        data={"an_image": (tempfile.TemporaryFile(), 'filename.jpg')},
        follow_redirects=True,
    )

    # return home so we have a valid redirect for the next request
    client.get('/') 
    
    rv2 = client.post(
        "/user/upload/",
        headers={'content-type':'multipart/form-data'},
        data={"an_image": (tempfile.TemporaryFile(), 'filename.jpg')},
        follow_redirects=True,
    )
    assert b'Image Saved!' in rv1.data
    assert b'File name not allowed!' in rv2.data


def test_view_image(client):
    user_data = {
        'first_name': 'john',
        'last_name':  'doe',
        'email': 'johnDoe@riki.com',
        'password': 'password',
        'confirm_password': 'password',
    }
    client.post(
        '/user/create/',
        data=user_data,
        follow_redirects=True
    )
    
    client.post('/user/login/', data=dict(
        email='johnDoe@riki.com',
        password='password'
    ), follow_redirects=True)

    fp = tempfile.NamedTemporaryFile(prefix='filename', suffix='.jpg', delete=False)

    img = Image.new("RGB", (100, 100))
    img.save(fp, "JPEG")
    fp.seek(0)

    client.get('/') # return home

    client.post(
        "/user/upload",
        headers={"Content-Type": "multipart/form-data"},
        data={"an_image": (fp, 'filename.jpg')},
        follow_redirects=True,
    )
    
    response = client.get("/img/filename.jpg/")

    assert response.status_code == 200

def test_user_images(client):
    user_data = {
        'first_name': 'john',
        'last_name':  'doe',
        'email': 'johnDoe@riki.com',
        'password': 'password',
        'confirm_password': 'password',
    }
    client.post(
        '/user/create/',
        data=user_data,
        follow_redirects=True
    )
    
    client.post('/user/login/', data=dict(
        email='johnDoe@riki.com',
        password='password'
    ), follow_redirects=True)

    client.post(
        "/user/upload/",
        headers={"Content-Type": "multipart/form-data"},
        data={
            'an_image' : (tempfile.TemporaryFile(), 'filename.jpg')
        },
        follow_redirects=True,
    )

    rv2 = client.get(
        '/user/images/',
        follow_redirects=True
    )
    assert b'filename.jpg' in rv2.data
    assert b'johnDoe%40riki.com' in rv2.data

def test_index_images(client):
    user_data = {
        'first_name': 'john',
        'last_name':  'doe',
        'email': 'johnDoe@riki.com',
        'password': 'password',
        'confirm_password': 'password',
    }
    client.post(
        '/user/create/',
        data=user_data,
        follow_redirects=True
    )
    
    client.post('/user/login/', data=dict(
        email='johnDoe@riki.com',
        password='password'
    ), follow_redirects=True)


    client.post(
        "/user/upload/",
        headers={"Content-Type": "multipart/form-data"},
        data={
            'an_image' : (tempfile.TemporaryFile(), 'filename1.jpg')
        },
        follow_redirects=True,
    )
    client.post(
        "/user/upload/",
        headers={"Content-Type": "multipart/form-data"},
        data={
            'an_image' : (tempfile.TemporaryFile(), 'filename2.jpg')
        },
        follow_redirects=True,
    )
    client.post(
        "/user/upload/",
        headers={"Content-Type": "multipart/form-data"},
        data={
            'an_image' : (tempfile.TemporaryFile(), 'filename3.jpg')
        },
        follow_redirects=True,
    )
    client.post(
        "/user/upload/",
        headers={"Content-Type": "multipart/form-data"},
        data={
            'an_image' : (tempfile.TemporaryFile(), 'filename4.jpg')
        },
        follow_redirects=True,
    )
    rv = client.get(
        '/img/'
    )

    assert b'filename1.jpg' in rv.data
    assert b'filename2.jpg' in rv.data
    assert b'filename3.jpg' in rv.data
    assert b'filename4.jpg' in rv.data
    assert b'johnDoe%40riki.com' in rv.data
    


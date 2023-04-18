import pytest
from unittest.mock import patch
import os
from Riki import app
import tempfile
from wiki.web.init_db import init_db
from wiki.web.userDAO import UserDao, UserDaoManager

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config["TESTING"] = True #sets testing to true, needed for Flask to return proper response
    app.config["PRIVATE"] = False #sets PRIVATE to false to disable user auth (see protect dectorator in users.py)
    app.config["WTF_CSRF_ENABLED"] = False #disables CSRF in WTForms so that we can simulate posts

    # Initialize the in-memory database
    init_db(db_path, force=True)
    with app.test_client() as client:
        client.db_path = db_path # Add the database path as an attribute of the client
        with app.app_context():
            pass #if we need stuff in app context we can do it here
        yield client
    os.close(db_fd)
    os.unlink(db_path)

#this fixture will create a page that we can test on, and destroy it when our
#test is over.  Check out the official pytest docs for more details on fixtures.
@pytest.fixture
def testpage():
    with open("content/testpage.md", "w") as testpage: #open a fresh file
        testpage.write("title: testpage\ntags: test dummy\n\nThis is a test page.") #write contents
        testpage.flush() #flush buffer so contents are actually written to file
        yield testpage #yield the fixutre
        os.unlink("content/testpage.md") #after our test is over, this code executes to delete the file.  anything after yeild in a fixture is cleanup
        

def test_home(client):
    rv = client.get('/', follow_redirects=True)
    assert b'Main' in rv.data
    
    #here we stub wiki.web.routes.current_wiki to a MagicMock (see official docs about MagicMock, its built into python.
    #note how we use the full module name to patch the source of the object. 
    #if we just did patch('current_wiki') that would only patch the reference in this file
    with patch('wiki.web.routes.current_wiki') as mock_current_wiki:
        mock_current_wiki.get.return_value = None
        rv = client.get("/", follow_redirects=True)
        assert b'You did not create any content yet. Your wiki recommends you, to do so now, as every user will see this page first, and you would want to make a good impression, wouldn\'t you?' in rv.data

def test_index(client):
    rv = client.get('/index/', follow_redirects=True)
    assert b'Page Index' in rv.data
    
def test_display_404(client):
    rv = client.get('/foo/', follow_redirects=True)
    assert rv.status_code == 404
    
def test_create_get(client):
    rv = client.get("/create/", follow_redirects=True)
    assert b'Create a new page' in rv.data
    
def test_create_post(client):
    #example of posting a form, in this case we get redirected
    rv = client.post("/create/", 
        headers={"Content-Type":"multipart/form-data"}, 
        data={"url":"bar"}
    )
    assert b'You should be redirected automatically to target URL: <a href="/edit/bar/">/edit/bar/</a>' in rv.data

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
    #another example of posting a form
    rv = client.post("/edit/testpage",
        headers={"Content-Type":"multipart/form-data"},
        data={"title":"testpage",
              "body": "i edited the testpage",
              "tags": "test, edited"
        },
        follow_redirects=True
    )
    
    
    assert b'&#34;testpage&#34; was saved.' in rv.data
    #this is to read the file and see if it was actually edited
    with open("content/testpage.md", "r") as filein:
        assert "i edited the testpage" in filein.read()

# def test_user_login_successful(client):
#     rv = client.post('/user/login/', data=dict(
#         email='lklklk@lklklk.com',
#         password='lklklk'
#     ), follow_redirects=True)
    
#     assert rv.status_code == 200
#     assert b'Page Index' in rv.data
#     assert b'Login successful.' in rv.data
#     assert current_user.name == "lklklk"

def test_user_login_nonexistent_user(client):
    rv = client.post('/user/login/',
        headers={"Content-Type":"multipart/form-data"},
        data=dict(
            email='wrongname@email.com',
            password='wrongpassword'
        ),
        follow_redirects=True
    )

    assert b'Login' in rv.data
    assert b'Sign up' in rv.data
    assert b'Errors occured verifying your input. Please check the marked fields below.' in rv.data

def test_user_login_incorrect_password(client):
    rv = client.post('/user/login/', data=dict(
        email='lklklk@lklklk.com',
        password='wrongpassword'
    ), follow_redirects=True)

    assert b'Login' in rv.data
    assert b'Sign up' in rv.data
    assert b'Errors occured verifying your input. Please check the marked fields below.' in rv.data
    
# def test_user_logout(client):
#     # Login first
#     rv = client.post('/user/login/', data=dict(
#         email='lklklk@lklklk.com',
#         password='lklklk'
#     ), follow_redirects=True)

#     rv = client.get('/user/logout/', follow_redirects=True)

#     assert b'Page Index' in rv.data
#     assert b'Logout successful.' in rv.data
#     assert current_user.is_authenticated == False

# def test_user_logout_requires_login(client):
#     # No login
#     rv = client.get('/user/logout', follow_redirects=True)
#     assert b'Please log in to access this page.' in rv.data

def test_user_index(client):
    with pytest.raises(TypeError):
        client.get('/user/', follow_redirects=True)

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
    
    # with app.app_context():
    #     rows = user_dao_manager.get_users()
    #     print(f'Teddy -> {rows}')
    # # assert 1 == 2
    # print(rv.data.decode('utf-8'))
    assert b'Sign up successful.' in rv.data

    

# def test_user_profile(client):
#     client.post('/user/login/', data=dict(
#         email='lklklk@lklklk.com',
#         password='lklklk'
#     ), follow_redirects=True)
    
#     rv = client.get('/user/profile/', follow_redirects=True)
#     assert b'Profile' in rv.data
#     assert b'Name:' in rv.data
#     assert b'lklklk' in rv.data

def test_user_create_failed(client):
    rv = client.post('/user/create/', data=dict(
        name='testName',
        password='testPassword',
        email=f'test@riki.com',
        confirm_password='testPassword'
    ), follow_redirects=True)

    assert b'Errors occured verifying your input. Please check the marked fields below.' in rv.data

def test_delete(client):
    pass

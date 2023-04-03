import pytest
from unittest.mock import patch
import os

from Riki import app
import wiki.web.routes
import tempfile

@pytest.fixture
def client():
    app.config["TESTING"] = True #sets testing to true, needed for Flask to return proper response
    app.config["PRIVATE"] = False #sets PRIVATE to false to disable user auth (see protect dectorator in users.py)
    app.config["WTF_CSRF_ENABLED"] = False #disables CSRF in WTForms so that we can simulate posts
    with app.test_client() as client:
        with app.app_context():
            pass #if we need stuff in app context we can do it here
        yield client

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
    
def test_upload_image(client):
    # login necessary
    client.post('/user/login/', data=dict(
        name='name',
        password='1234'
    ), follow_redirects=True)

    # send the request
    rv = client.post("/user/name/upload", headers={"Content-Type":"multipart/form-data"},
        data = {
            "an_image" : tempfile.NamedTemporaryFile(suffix=".jpg")
        }, 
        follow_redirects=True
    )

    # big win
    assert b"Image Saved" in rv.data

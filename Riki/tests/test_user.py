import pytest
from wiki.web.user import User, UserManager

@pytest.fixture
def manager():
  manager = UserManager('.')
  data = {'authenticated': True, 'active': True, 'name': 'Abebe'}
  manager.data = data
  yield manager

@pytest.fixture
def user(manager):
  user = User(manager, 'Abebe', manager.data)
  yield user

def test_user_constructor(manager, user):
  assert user.manager == manager

def test_get(user):
  assert user.get('authenticated') == True
  assert user.get('active') == True
  assert user.get('name') == 'Abebe'

def test_set(user):
  user.set('authenticated', False)
  assert user.get('authenticated') == False

def test_save(manager, user):
  user.set('authenticated', False)
  response = manager.read().get('Abebe')
  assert response['authenticated'] == False

def test_is_authenticated(user):
  assert user.is_authenticated() == True

def test_is_active(user):
  assert user.is_active() == True

def test_is_anonymous(user):
  assert user.is_anonymous() == False

def test_get_id(user):
  assert user.get_id() == "Abebe"

def test_check_password_cleartext(manager):
  # Test get_default_authentication_method: cleartext
  password = "passwordAbebe"
  user_data = {'authentication_method': 'cleartext', 'name': 'Abebe', 'password' : "passwordAbebe"}
  user = User(manager, 'Abebe', user_data)
  assert user.check_password(password) == True

# def test_check_password_hash(manager):
#   # Test get_default_authentication_method: cleartext
#   password = "passwordAbebe"
#   user_data = {'authentication_method': 'hash', 'name': 'Abebe', 'password' : "passwordAbebe"}
#   user = User(manager, 'Abebe', user_data)
#   assert user.check_password(password) == True

def test_check_password_authentication_method_not_implemented(manager):
  # Test authentication_method: not_implemented
  password = "passwordAbebe"
  user_data = {'authentication_method': 'unknown', 'name': 'Abebe', 'password' : "passwordAbebe"}
  user = User(manager, 'Abebe', user_data)
  with pytest.raises(NotImplementedError):
    user.check_password(password)

def test_get_default_authentication_method():
  pass


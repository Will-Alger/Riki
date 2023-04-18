import sqlite3
from wiki.web.db import get_db
from werkzeug.security import generate_password_hash

class UserDao(object):
  def __init__(self, name, email, password, manager):
    
    self.manager = manager
    self.data = {
      "name" : name,
      "email" : email,
      "hashed_password" : generate_password_hash(password),
      "authenticated" : False,
    }

  def is_authenticated(self):
    return self.data['authenticated']

  def is_active(self):
    return True

  def is_anonymous(self):
    return False
  
  def get_id(self):
    return self.manager.get_user(self.data['name'])
  
  def check_password(self, password):
    return generate_password_hash(password) == self.manager.get_password(self.get_id)
  
  def set(self, option, value):
    self.data[option] = value
    self.save()

  def save(self):
    self.manager.cur.execute(
      "UPDATE users SET name = (?), email = (?), password = (?) WHERE id = (?)",
      (self.data['name'], self.data['email'], self.data['hashed_password'], self.get_id())
    )

  


class UserDaoManager(object):
  def __init__(self, path):
    self.connection = get_db()
    self.cur = self.connection.cursor()

  def create_user(self, user):
    self.cur.execute(
      "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
      (user.data['name'], user.data['email'], user.data['hashed_password'])
    )
    self.connection.commit()

    

  def get_users(self):
    self.connection.row_factory = sqlite3.Row
    cur = self.connection.cursor()
    cur.execute(
      "SELECT * FROM users"
    )
    result = cur.fetchall()
    return result
  
  def get_user(self, name):
    self.cur.execute(
      "SELECT id FROM users WHERE name = (?)", ((name,))
    )
    return self.cur.fetchone()

  def close_db(self):
    self.connection.close()

  def update(self, name, userdata):
    data = self.get_users()
    data[name] = userdata
    self.write[data]

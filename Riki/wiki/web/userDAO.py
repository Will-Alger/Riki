import sqlite3
import uuid

class UserDao(object):
  def __init__(self, name, email, password):
    self.id = str(uuid.uuid4())
    self.name = name
    self.email = email
    self.password = password
    self.authenticated = False

  def is_authenticated(self):
    return self.authenticated

  def is_active(self):
    return True

  def is_anonymous(self):
    return False
  
  def get_id(self):
    return self.name


class UserDaoManager(object):
  def __init__(self, path):
    self.connection = sqlite3.connect(path)
    self.cur = self.connection.cursor()
    self.table_name = "users"

  def create_user(self, user):
    self.cur.execute(
      "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
      (user.name, user.email, user.password)
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
  
  def get_user(self, email):
    self.cur.execute(
      "SELECT email FROM users WHERE email = (?)", ((email,))
    )
    return self.cur.fetchone()

  def close_db(self):
    self.connection.close()

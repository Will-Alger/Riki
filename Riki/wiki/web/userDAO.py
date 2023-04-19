import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from wiki.web.db import *


class UserDao(object):
  def __init__(self, first_name, last_name, email, password):
    self.first_name = first_name
    self.last_name = last_name
    self.email = email
    self.password = password
    self.authenticated = False
    self.manager = UserDaoManager('/var/db/riki.db')
    self.active = True
  
  def set_authenticated(self, value):
      self.authenticated = value

  def is_authenticated(self):
    return self.data['authenticated']

  def is_active(self):
    return self.active

  def is_anonymous(self):
    return False
  
  def get_id(self):
    return self.email
  
  def check_password(self, password):
    return check_password_hash(self.password, password)


class UserDaoManager(object):
  def __init__(self, path):
      self.connection = get_db()
      self.cur = self.connection.cursor()

  def create_user(self, user):
    hashedPassword = generate_password_hash(user.password, method='sha256')
    self.cur.execute(
      "INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
      (user.first_name, user.last_name, user.email, hashedPassword)
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
      "SELECT * FROM users WHERE email = (?)", ((email,))
    )
    user = self.cur.fetchone()
    if user is None:
      return None
    else:
      return UserDao(user[1], user[2], user[3], user[4])
  
  def delete_all_users(self):
    self.cur.execute("DELETE FROM users")
    self.connection.commit()
  
  def delete_user(self, email):
    user = self.get_user(email)
    if user is not None:
      self.cur.execute(
        "DELETE FROM users WHERE email = (?)", ((email,))
      )
      self.connection.commit()
      return True
    else:
      return False

  def close_db(self):
    self.connection.close()

  def update(self, name, userdata):
    data = self.get_users()
    data[name] = userdata
    self.write[data]

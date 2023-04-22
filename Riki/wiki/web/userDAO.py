import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from wiki.web.db import *
from functools import wraps
from flask import current_app
from flask_login import current_user


class UserDao(object):
  def __init__(self, first_name, last_name, email, password, signup_time):
    self.first_name = first_name
    self.last_name = last_name
    self.email = email
    self.password = password
    self.authenticated = False
    self.active = True
    self.signup_time = signup_time
  
  def set_authenticated(self, value):
      self.authenticated = value

  def is_authenticated(self):
    return self.authenticated

  def is_active(self):
    return self.active

  def is_anonymous(self):
    return False
  
  def get_id(self):
    return self.email
  
  def check_password(self, password):
    return check_password_hash(self.password, password)


class UserDaoManager(object):
  def __init__(self):
      self.connection = get_db()
      self.cur = self.connection.cursor()

  def create_user(self, user):
    hashedPassword = generate_password_hash(user.password, method='sha256')
    self.cur.execute(
      "INSERT INTO users (first_name, last_name, email, password, created) VALUES (?, ?, ?, ?, ?)",
      (user.first_name, user.last_name, user.email, hashedPassword, user.signup_time)
    )
    self.connection.commit()

  def get_users(self):
    self.cur.execute(
      "SELECT * FROM users"
    )
    result = self.cur.fetchall()
    return result
  
  def get_user(self, email):
    self.cur.execute(
      "SELECT * FROM users WHERE email = (?)", ((email,))
    )
    user = self.cur.fetchone()
    if user is None:
      return None
    else:
      return UserDao(user[1], user[2], user[3], user[4], user[5])
  
  def update_user(self, current_user_email, updated_first_name, updated_last_name):
    self.cur.execute(
      "UPDATE users SET first_name=?, last_name=? WHERE email = (?)",
      (updated_first_name, updated_last_name, current_user_email)
    )
    self.connection.commit()
  
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
  
  def record_history(self, email, page_url, edit_time):
    self.cur.execute(
    "INSERT INTO user_edit_history (user_email, page_url, edit_time) VALUES (?, ?, ?)",
    (email, page_url, edit_time)
    )
    self.connection.commit()
  
  def get_edit_history(self, email):
    user = self.get_user(email)
    if user is not None:
      self.cur.execute(
        "SELECT * FROM user_edit_history WHERE user_email = (?)", ((email,))
      )
      return self.cur.fetchall()
    else:
      return None

  def close_db(self):
    self.connection.close()

def protect(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
      if current_app.config.get("PRIVATE") and not current_user.is_authenticated:
          return current_app.login_manager.unauthorized()
      return f(*args, **kwargs)

  return wrapper

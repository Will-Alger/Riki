import sqlite3
import uuid
from wiki.web.userDAO import UserDaoManager
from wiki.web.db import *


class ImageDAO(object):
    def __init__(self):
        self.connection = get_db()
        self.cur = self.connection.cursor()
        self.userDAO = UserDaoManager('/var/db/riki.db')

    def save_image(self, filename, userID):
        
        self.userDAO.get_user(userID)
        self.cur.execute(
            """INSERT INTO images (filename, userid) VALUES (?, ?)""",
            (filename, userID)
        )
        self.connection.commit()

    def get_user_images(self, user):
        self.cur.execute(
            "SELECT * FROM images WHERE userID = (?)", ((self.userDAO.get_user(user)))
        )
        return self.cur.fetchall()
    
    def close_db(self):
        self.connection.close()
        self.userDAO.close_db()  

    def filename_exists(self, filename):
        self.cur.execute(
            "SELECT EXISTS(SELECT 1 FROM images WHERE filename = (?))", ((filename,))
        )  
        return self.cur.fetchone() == 1

    def get_image_owner(self, filename):
        self.cur.execute(
            """SELECT 1 FROM users WHERE id = (SELECT userid FROM images WHERE filename = ?)""", 
            (filename,)
        )
        return self.cur.fetchone()

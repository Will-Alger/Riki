import sqlite3
from wiki.web.db import *


class ImageDAO(object):
    def __init__(self):
        self.connection = get_db()
        self.cur = self.connection.cursor()

    def save_image(self, filename, email):
        """
        this method adds an image associated with an email to the database
        """
        self.cur.execute(
            """INSERT INTO images (filename, email) VALUES (?, ?)""",
            (filename, email)
        )
        self.connection.commit()

    def get_user_images(self, email):
        self.cur.execute(
            "SELECT * FROM images WHERE email = (?)", ((email,))
        )
        return self.cur.fetchall()
    
    def close_db(self):
        self.connection.close() 

    def filename_exists(self, filename):
        self.cur.execute(
            "SELECT 1 FROM images WHERE filename = (?)", ((filename,))
        )  
        return self.cur.fetchone() is not None

    def get_image_owner(self, filename):
        self.cur.execute(
            """SELECT email FROM images WHERE filename = ?""", 
            (filename,)
        )
        return self.cur.fetchone()

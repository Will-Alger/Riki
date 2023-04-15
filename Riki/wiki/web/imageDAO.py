import sqlite3
import uuid
from wiki.web.userDAO import UserDaoManager


class ImageDAO(object):
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.cur = self.connection.cursor()
        self.userDAO = UserDaoManager('/var/db/riki.db')

    def save_image(self, filename, userID):
        
        self.cur.execute(
            "INSERT INTO images (id, filename, userid) VALUES (?, ?, ?)",
            (str(uuid.uuid4()), filename, userID)
        )
        self.connection.commit()

    def get_user_images(self, user):
        self.cur.execute(
            "SELECT * FROM images WHERE userID = (?)", ((self.userDAO.get_user(user)))
        )
        return self.cur.fetchone()
    
    def close_db(self):
        self.connection.close()
        self.userDAO.close_db()    


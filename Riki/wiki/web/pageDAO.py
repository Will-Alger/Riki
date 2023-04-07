import sqlite3

class PageDaoManager(object):
    def __init__(self, path):
      self.connection = sqlite3.connect(path)
      self.cur = self.connection.cursor()

    def save_page(self, page):
      self.cur.execute("INSERT OR IGNORE INTO pages (doc_id, title, body) VALUES (?, ?, ?)", (page.id, page.title, page.body))
          

    def update_page_index(self, page):
      page_index = page.tokenize_and_count()
      cur

    
    

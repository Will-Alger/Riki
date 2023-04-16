import sqlite3
from wiki.web.db import *


class PageDaoManager(object):
    def __init__(self):
        self.connection = get_db()
        self.cur = self.connection.cursor()

    def update_page_index(self, page):
        page_index = page.tokenize_and_count()
        self.delete_old_tokens(page, page_index)
        self.add_or_update_tokens(page, page_index)
        self.connection.commit()

    def delete_old_tokens(self, page, page_index):
        self.cur.execute(
            """
          DELETE FROM page_index
          WHERE doc_id = ? AND word NOT IN ({})
      """.format(
                ", ".join("?" for _ in page_index)
            ),
            [page.id] + list(page_index.keys()),
        )

    def add_or_update_tokens(self, page, page_index):
        for token, frequency in page_index.items():
            self.cur.execute(
                "INSERT OR REPLACE INTO page_index (word, doc_id, frequency) VALUES (?,?,?)",
                (token, page.id, frequency),
            )

    def update_page_index_id(self, new_id, old_id):
        # Update the "doc_id" value in the "page_index" table for the old page to the ID of the new page
        self.cur.execute(
            "UPDATE page_index SET doc_id = ? WHERE doc_id = ?", (new_id, old_id)
        )
        self.connection.commit()

    def delete(self, page):
        # Remove rows from the page_index table where doc_id = page.id
        self.cur.execute("DELETE FROM page_index WHERE doc_id=?", (page.id,))
        self.connection.commit()

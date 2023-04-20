from wiki.web.db import *


class PageDaoManager(object):
    def __init__(self):
        self.connection = get_db()
        self.cur = self.connection.cursor()

    def update_page_index(self, page):
        """
        Updates the page_index table for a given page by deleting the old tokens and adding or updating the new ones.

        Args:
            page (Page): The page object.

        Returns:
            None

        """
        page_index = page.tokenize_and_count()

        # Delete the old tokens from the page_index table
        self.delete_old_tokens(page, page_index)

        # Add or update the new tokens in the page_index table
        self.add_or_update_tokens(page, page_index)

        # Commit the changes to the database
        self.connection.commit()

    def delete_old_tokens(self, page, new_page_index):
        """
        Deletes tokens from the page_index table for a given page that are not included in the new page index.

        Args:
            page (Page): The page object.
            page_index (dict): A dictionary containing tokens and their frequencies to be included in the new page index.

        Returns:
            None

        """
        # Get the current tokens for the page using the get_tokens method
        current_index = self.get_tokens(page)

        # Find the tokens to be deleted by getting the difference between the current tokens and the new page index
        tokens_to_delete = set(current_index.keys()) - set(new_page_index.keys())

        # Check if there are any tokens to delete, if not, return
        if not tokens_to_delete:
            return

        # Construct a SQL query to delete tokens that are in tokens_to_delete and match the given page's ID
        self.cur.execute(
            """
            DELETE FROM page_index
            WHERE doc_id = ? AND word IN ({})
        """.format(
                ", ".join("?" for _ in tokens_to_delete)
            ),
            [page.id] + list(tokens_to_delete),
        )

    def add_or_update_tokens(self, page, page_index):
        """
        Adds or updates the token frequency in the page_index table for a given page.

        Args:
            page (Page): The page object.
            page_index (dict): A dictionary containing tokens and their frequencies
                                to be added or updated for the given page.

        Returns:
            None

        """
        # Iterate over each token and its frequency in the page index
        for token, frequency in page_index.items():
            # Add or update the token's frequency for the given page in the page_index table
            self.cur.execute(
                "INSERT OR REPLACE INTO page_index (word, doc_id, frequency) VALUES (?,?,?)",
                (token, page.id, frequency),
            )
        # Commit the changes to the database
        self.connection.commit()

    def update_page_index_id(self, new_id, old_id):
        """
        Update the "doc_id" value in the "page_index" table for the old page to the ID of the new page.

        Args:
            new_id (int): The ID of the new page that will replace the old page's ID.
            old_id (int): The ID of the old page that will be replaced by the new page's ID.

        Returns:
            None

        """
        # Execute the SQL statement to update the "doc_id" value in the "page_index" table.
        self.cur.execute(
            "UPDATE page_index SET doc_id = ? WHERE doc_id = ?", (new_id, old_id)
        )

        # Commit the changes to the database.
        self.connection.commit()

    def get_tokens(self, page):
        """
        Retrieves the tokens for a given page from the page_index table in the database.

        :param page: Page object representing the page to retrieve tokens for.
        :return: Dictionary containing words as keys and their corresponding frequencies as values.
        """
        # Query the database for the updated tokens and convert to a dictionary
        tokens_dict = {
            word: frequency
            for word, frequency in self.cur.execute(
                "SELECT word, frequency FROM page_index WHERE doc_id=?", (page.id,)
            ).fetchall()
        }
        return tokens_dict

    def delete(self, page):
        """
        This method deletes rows from the page_index table corresponding to
        the provided page object by using its 'id' attribute.

        Args:
        - page: The Page object to be deleted from database

        Returns:
        - None
        """
        # Remove rows from the page_index table where doc_id = page.id
        self.cur.execute("DELETE FROM page_index WHERE doc_id=?", (page.id,))

        # Commit changes to update the database
        self.connection.commit()

    def search(self, search_terms, ignore_case=True):
        """
        Searches for pages containing all of the provided search terms.

        Args:
            search_terms (list[str]): A list of search terms to be searched.
            ignore_case (bool): Set to True to ignore case sensitivity while searching.

        Returns:
            dict[string, int]: A dictionary containing doc_id as the key and total_frequency as the value for matching pages.

        """
        if ignore_case:
            search_terms = [term.lower() for term in search_terms]
            word_compare = "LOWER(word)"

        else:
            word_compare = "word"

        # Build a SQL query string to retrieve the documents that match the search terms
        query = f"""
            SELECT doc_id, SUM(frequency) as total_frequency
            FROM page_index
            WHERE {word_compare} IN ({', '.join('?' for _ in search_terms)})
            GROUP BY doc_id
            ORDER BY total_frequency DESC
            """

        # Execute the query and fetch all results
        results = self.cur.execute(query, search_terms).fetchall()

        # Convert the results into a dictionary
        result_dict = {row[0]: row[1] for row in results}

        return result_dict

from Riki import app
import os
import tempfile
import unittest
import sqlite3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pytest
from wiki.web.pageDAO import PageDaoManager
from wiki.web.db import *


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config["DATABASE"] = db_path
    app.config["TESTING"] = True
    app.config[
        "PRIVATE"
    ] = False  # sets PRIVATE to false to disable user auth (see protect dectorator in users.py)
    app.config[
        "WTF_CSRF_ENABLED"
    ] = False  # disables CSRF in WTForms so that we can simulate posts
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def dao(client):
    with app.app_context():
        dao_manager = PageDaoManager()
    yield dao_manager


class MockPage:
    def __init__(self, id):
        self.id = id


def test_update_page_index_id(client, dao):
    # Create two page objects with distinct ids, one of which will be updated to a new id
    old_id = "old_id"
    new_id = "new_id"
    old_page_id = MockPage("old_id")
    new_page_id = MockPage("new_id")

    # Define a sample page index dictionary
    page_index = {"word1": 3, "word2": 2, "word3": 1}

    # Add the sample page index to the database for the old page id
    dao.add_or_update_tokens(old_page_id, page_index)

    # Call the method being tested to update the page id
    dao.update_page_index_id(new_id, old_id)

    # Get the tokens associated with the old page id (which should now be empty)
    result1 = dao.get_tokens(old_page_id)
    assert len(result1) == 0

    # Get the tokens associated with the new page id (which should contain the original tokens)
    result2 = dao.get_tokens(new_page_id)
    assert len(result2) == 3
    assert result2 == page_index


def test_delete_old_tokens(client, dao):
    # Define old and new page index and expected index
    old_page_index = {"word1": 3, "word2": 2, "word3": 1}
    new_page_index = {"word1": 4, "word4": 5}
    expected_index = {"word1": 3}

    # Create a mock page object with ID 'testid'
    page = MockPage("testid")

    # Insert old_page_index values into the database
    dao.add_or_update_tokens(page, old_page_index)

    # Call delete_old_tokens with new_page_index
    dao.delete_old_tokens(page, new_page_index)

    # Get current tokens from the database
    result = dao.get_tokens(page)

    # Check that the returned tokens match the expected ones
    assert result == expected_index


def test_add_or_update_tokens(client, dao):
    init_tokens = {"word1": 3, "word2": 2}
    updated_tokens = {"word1": 4, "word2": 1, "word3": 5}
    page = MockPage("testid")

    # Insert intial tokens into the database
    dao.add_or_update_tokens(page, init_tokens)

    # Insert the same tokens with different values
    dao.add_or_update_tokens(page, updated_tokens)

    updated_tokens_dict = dao.get_tokens(page)

    # Check if the updated tokens match the updated_page_index
    assert updated_tokens_dict == updated_tokens


def test_get_tokens(client, dao):
    init_tokens = {"word1": 3, "word2": 2}
    page = MockPage("testid")

    # Insert intial tokens into the database
    dao.add_or_update_tokens(page, init_tokens)
    tokens = dao.get_tokens(page)

    assert tokens == init_tokens


def test_delete(client, dao):
    init_tokens = {"word1": 3, "word2": 2}
    page = MockPage("testid")

    # Insert intial tokens into the database
    dao.add_or_update_tokens(page, init_tokens)

    # Delete all the rows with the page.id
    dao.delete(page)

    # get all the tokens from the database with the page.id

    tokens = dao.get_tokens(page)

    # assert tokens is empty
    assert len(tokens) == 0


def test_search_empty(client, dao):
    # Test searching for an empty list of search terms
    result_dict = dao.search([], ignore_case=False)
    assert len(result_dict) == 0


def test_search_nonexistent_terms(client, dao):
    # Define a sample page index dictionary
    page_index1 = {"word1": 3, "word2": 2, "word3": 1}

    # Create a mock page with a distinct id
    page1 = MockPage("page1")

    # Insert the sample page index into the database for the page
    dao.add_or_update_tokens(page1, page_index1)


def test_search_case_sensitive(client, dao):
    # Define sample page index dictionaries with different capitalizations of the same words
    page_index1 = {"word1": 3, "Word2": 2, "wOrd3": 1}
    page_index2 = {"WORD1": 4, "word2": 1, "Word3": 5}

    # Create two mock pages with distinct ids
    page1 = MockPage("page1")
    page2 = MockPage("page2")

    # Insert the sample page indexes into the database for the two pages
    dao.add_or_update_tokens(page1, page_index1)
    dao.add_or_update_tokens(page2, page_index2)

    # Test a case-sensitive search for "word1" and "Word2"
    result_dict = dao.search(["word1", "Word2"], ignore_case=False)
    assert len(result_dict) == 1
    assert result_dict[page1.id] == 5

    # Test a case-sensitive search for "WORD1" and "word2"
    result_dict = dao.search(["WORD1", "word2"], ignore_case=False)
    assert len(result_dict) == 1
    assert result_dict[page2.id] == 5


def test_search_case_insensitive(client, dao):
    # Define sample page index dictionaries with different capitalizations of the same words
    page_index1 = {"word1": 3, "Word2": 2, "wOrd3": 1}
    page_index2 = {"WORD1": 4, "word2": 1, "Word3": 5}

    # Create two mock pages with distinct ids
    page1 = MockPage("page1")
    page2 = MockPage("page2")

    # Insert the sample page indexes into the database for the two pages
    dao.add_or_update_tokens(page1, page_index1)
    dao.add_or_update_tokens(page2, page_index2)

    # Test a case-insensitive search for "word1" and "Word2"
    result_dict = dao.search(["word1", "Word2"], ignore_case=True)
    assert len(result_dict) == 2
    assert result_dict[page1.id] == 5
    assert result_dict[page2.id] == 5

    # Test a case-insensitive search for "WORD1" and "word2"
    result_dict = dao.search(["WORD1", "word2"], ignore_case=True)
    assert len(result_dict) == 2
    assert result_dict[page1.id] == 5
    assert result_dict[page2.id] == 5


def test_search_returns_results_in_descending_order(client, dao):
    # Define sample page index dictionaries
    page_index1 = {"word1": 3, "word2": 2, "word3": 1}
    page_index2 = {"word1": 5, "word2": 4, "word3": 6}
    page_index3 = {"word1": 22, "word2": 4, "word3": 6}

    # Create two mock pages with distinct ids
    page1 = MockPage("page1")
    page2 = MockPage("page2")
    page3 = MockPage("page3")

    # Insert the sample page indexes into the database for the two pages
    dao.add_or_update_tokens(page1, page_index1)
    dao.add_or_update_tokens(page2, page_index2)
    dao.add_or_update_tokens(page3, page_index3)

    # Search for the terms and check if the frequencies are in descending order
    result_dict = dao.search(["word1", "word2", "word3"], ignore_case=True)
    assert len(result_dict) == 3

    first_frequency = None
    for frequency in result_dict.values():
        if first_frequency is not None:
            assert frequency <= first_frequency
        first_frequency = frequency

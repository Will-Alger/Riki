from Riki import app
import wiki.web.init_db
from wiki.web.init_db import init_db
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
def page_dao_manager(client):
    with app.app_context():
        dao_manager = PageDaoManager()
    yield dao_manager


class MockPage:
    def __init__(self, id):
        self.id = id


def test_page_delete(client, page_dao_manager):
    page = MockPage("testid")
    page_dao_manager.cur.execute(
        "INSERT INTO page_index (word, doc_id, frequency) VALUES (?, ?, ?)",
        ("word", "testid", 5),
    )
    page_dao_manager.delete(page)
    result = page_dao_manager.cur.execute(
        "SELECT * FROM page_index WHERE doc_id=?", (page.id,)
    ).fetchone()
    assert result is None


def test_update_page_index_id(client, page_dao_manager):
    old_id = "old_id"
    new_id = "new_id"

    # Insert multiple sample rows with the old_id
    sample_rows = [("word1", old_id, 5), ("word2", old_id, 3), ("word3", old_id, 2)]
    page_dao_manager.cur.executemany(
        "INSERT INTO page_index (word, doc_id, frequency) VALUES (?, ?, ?)", sample_rows
    )

    # Call the update_page_index_id method to update the doc_id
    page_dao_manager.update_page_index_id(new_id, old_id)

    # Query the table to check if all the old_id values are updated to the new_id
    updated_results = page_dao_manager.cur.execute(
        "SELECT * FROM page_index WHERE doc_id=?", (new_id,)
    ).fetchall()

    assert len(updated_results) == len(sample_rows)

    for result, sample_row in zip(updated_results, sample_rows):
        assert result["doc_id"] == new_id
        assert result["word"] == sample_row[0]
        assert result["frequency"] == sample_row[2]

    # Check if the old_id is no longer in the table
    with app.app_context():
        result_old = page_dao_manager.cur.execute(
            "SELECT * FROM page_index WHERE doc_id=?", (old_id,)
        ).fetchall()

    assert len(result_old) == 0


def test_delete_old_tokens(client, page_dao_manager):
    old_page_index = {"word1": 3, "word2": 2, "word3": 1}
    new_page_index = {"word1": 4, "word4": 5}
    page = MockPage("testid")

    # Insert old_page_index values into the database
    for word, frequency in old_page_index.items():
        page_dao_manager.cur.execute(
            "INSERT INTO page_index (word, doc_id, frequency) VALUES (?, ?, ?)",
            (word, page.id, frequency),
        )

    # Call delete_old_tokens with new_page_index
    page_dao_manager.delete_old_tokens(page, new_page_index)

    # Insert new_page_index values into the database
    for word, frequency in new_page_index.items():
        page_dao_manager.cur.execute(
            "INSERT OR REPLACE INTO page_index (word, doc_id, frequency) VALUES (?, ?, ?)",
            (word, page.id, frequency),
        )

    # Query the database for the remaining tokens and convert to a dictionary
    remaining_tokens_dict = {
        word: frequency
        for word, frequency in page_dao_manager.cur.execute(
            "SELECT word, frequency FROM page_index WHERE doc_id=?", (page.id,)
        ).fetchall()
    }

    # Check if the remaining tokens match the new_page_index
    assert remaining_tokens_dict == new_page_index


def test_add_or_update_tokens(client, page_dao_manager):
    initial_page_index = {"word1": 3, "word2": 2}
    updated_page_index = {"word1": 4, "word2": 1, "word3": 5}
    page = MockPage("testid")

    # Insert initial_page_index values into the database
    for word, frequency in initial_page_index.items():
        page_dao_manager.cur.execute(
            "INSERT INTO page_index (word, doc_id, frequency) VALUES (?, ?, ?)",
            (word, page.id, frequency),
        )

    # Call add_or_update_tokens with updated_page_index
    page_dao_manager.add_or_update_tokens(page, updated_page_index)

    # Query the database for the updated tokens and convert to a dictionary
    updated_tokens_dict = {
        word: frequency
        for word, frequency in page_dao_manager.cur.execute(
            "SELECT word, frequency FROM page_index WHERE doc_id=?", (page.id,)
        ).fetchall()
    }

    # Check if the updated tokens match the updated_page_index
    assert updated_tokens_dict == updated_page_index


CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT UNIQUE NOT NULL,
    userid INTEGER NOT NULL
);

CREATE TABLE page_index (
    word TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    frequency INTEGER NOT NULL,
    PRIMARY KEY (word, doc_id)
);
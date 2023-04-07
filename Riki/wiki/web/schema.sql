
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE pages (
     doc_id TEXT NOT NULL PRIMARY KEY,
     title TEXT,
     context TEXT
);

CREATE TABLE page_index (
    word TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    frequency INTEGER NOT NULL,
    PRIMARY KEY (word, doc_id),
    FOREIGN KEY (doc_id) REFERENCES pages (doc_id) ON DELETE CASCADE
);
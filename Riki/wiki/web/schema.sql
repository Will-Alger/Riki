
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE page_index (
    word TEXT NOT NULL,
    doc_id TEXT NOT NULL,
    frequency INTEGER NOT NULL,
    PRIMARY KEY (word, doc_id)
);

CREATE TABLE user_edit_history(
    user_email TEXT NOT NULL,
    page_url TEXT NOT NULL,
    edit_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
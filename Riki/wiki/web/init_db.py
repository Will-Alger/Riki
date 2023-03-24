import sqlite3
import os

def init_db(dbpath='/var/db/riki.db', force=False):
    if not os.path.exists(dbpath) or force:
        print(" * database not found -> running init_db.py")

    # Connect to the database
    with sqlite3.connect(dbpath) as connection:

        # Create tables from schema.sql
        with open('wiki/web/schema.sql') as f:
            connection.executescript(f.read())

        # Insert sample data
        cur = connection.cursor()
        cur.executemany("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                        [('john doe', 'john.doe@example.com', 'password123'),
                            ('bob smith', 'bob.smith@example.com', 'password789')]
                        )

        # Fetch all users and print them
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        for row in rows:
            print(row)

        # Commit changes and close the connection
        connection.commit()

    # else:
        print(" * database found -> skipping init_db.py")
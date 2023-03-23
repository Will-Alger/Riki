import sqlite3
import os

dbpath = "/var/db/riki.db"

if (not os.path.exists(dbpath)):
    print(" * database not found, running int_db.py")
    
    # how to make connection string to var/db
    connection = sqlite3.connect("/var/db/riki.db")

    with open('wiki/web/schema.sql') as f:
        connection.executescript(f.read())

    cur = connection.cursor()

    cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                ('john doe', 'john.doe@example.com', 'password123')
                )

    cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                ('bob smith', 'bob.smith@example.com', 'password789')
                )



    cur = connection.cursor()
    cur.execute("SELECT * FROM users")

    rows = cur.fetchall()

    for row in rows:
        print(row)

    connection.commit()
    connection.close()
else:
    print(" * database found, skipping init_db.py")
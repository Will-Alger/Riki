import sqlite3

#TODO only init if riki.db doesn't exist in /var/db

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
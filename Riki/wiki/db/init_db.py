import sqlite3

connection = sqlite3.connect("riki.db")

with open('Riki/wiki/db/schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO user (name, email, password) VALUES (?, ?, ?)",
            ('john doe', 'john.doe@example.com', 'password123')
            )

cur.execute("INSERT INTO user (name, email, password) VALUES (?, ?, ?)",
            ('bob smith', 'bob.smith@example.com', 'password789')
            )



cur = connection.cursor()
cur.execute("SELECT * FROM user")

rows = cur.fetchall()

for row in rows:
    print(row)

connection.commit()
connection.close()
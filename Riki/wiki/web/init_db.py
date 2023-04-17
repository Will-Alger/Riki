# import sqlite3
# import os


# def init_db(dbpath="/var/db/riki.db", force=False):
#     if not os.path.exists(dbpath) or force:
#         print(" * database not found -> running init_db.py")

#         # Connect to the database
#         with sqlite3.connect(dbpath) as connection:
#             # Create tables from schema.sql
#             with open("wiki/web/schema.sql") as f:
#                 connection.executescript(f.read())

#             # Commit changes and close the connection
#             connection.commit()

#     else:
#         print(" * database found -> skipping init_db.py")

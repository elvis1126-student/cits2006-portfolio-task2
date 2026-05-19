import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS comments")

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT
)
""")

# weak credentials (intentional)
cursor.execute("INSERT INTO users (username, password) VALUES ('admin', '1234')")
cursor.execute("INSERT INTO users (username, password) VALUES ('user', 'password')")

conn.commit()
conn.close()

print("Database ready ✅")
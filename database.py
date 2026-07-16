import sqlite3

conn = sqlite3.connect("aipds.db")
cursor = conn.cursor()

# ================= USERS TABLE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# ================= UPLOADS TABLE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    filename TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_records INTEGER,
    fraud_count INTEGER,
    safe_count INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

# ================= PREDICTIONS TABLE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upload_id INTEGER,
    record_number INTEGER,
    prediction TEXT,
    FOREIGN KEY(upload_id) REFERENCES uploads(id)
)
""")

conn.commit()
conn.close()

print("✅ Database Created Successfully!")
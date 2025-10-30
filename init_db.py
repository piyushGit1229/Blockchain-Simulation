import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Create users table with all necessary columns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        private_key TEXT UNIQUE NOT NULL,
        balance REAL DEFAULT 100,
        wallet_balance REAL DEFAULT 0,
        public_key TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("database.db initialized successfully.")

if __name__ == "__main__":
    init_db()

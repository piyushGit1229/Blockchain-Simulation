import sqlite3

def init_contracts():
    conn = sqlite3.connect("contracts.db")
    cursor = conn.cursor()

    # Create contracts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        recipient TEXT,
        amount REAL,
        execution_time TEXT,
        is_processed INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print("contracts.db initialized successfully.")

if __name__ == "__main__":
    init_contracts()

import sqlite3


def init_contracts_db():
    conn = sqlite3.connect("contracts.db")
    cursor = conn.cursor()

    # Create the smart_contracts table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS smart_contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'active'  -- Can be 'active' or 'inactive'
    )
    """)

    conn.commit()
    conn.close()

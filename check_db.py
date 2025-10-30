import sqlite3

# Check database.db
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
result = cursor.fetchone()
print("database.db users table schema:")
print(result[0] if result else "No users table found")
conn.close()

# Check contracts.db
conn = sqlite3.connect("contracts.db")
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='contracts'")
result = cursor.fetchone()
print("\ncontracts.db contracts table schema:")
print(result[0] if result else "No contracts table found")
conn.close()

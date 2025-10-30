# Database Setup Instructions for Cloned Project

If you're having issues setting up the databases after cloning the project, follow these steps:

## Step 1: Install Dependencies
```
pip install -r requirements.txt
```

## Step 2: Initialize the Main Database
Run the database initialization script:
```
python init_db.py
```
This will create the `database.db` file with the `users` table that includes columns for id, username, password, private_key, balance, wallet_balance, and public_key.

## Step 3: Initialize the Contracts Database
Run the contracts database initialization script:
```
python init_contracts.py
```
This will create the `contracts.db` file with the `contracts` table that includes columns for id, sender, recipient, amount, execution_time, is_processed, and created_at.

## Step 4: Verify Database Setup
To verify that the databases are set up correctly, run:
```
python check_db.py
```
This will display the schema of both tables.

## Step 5: Run the Application
Start the Flask application:
```
python routes.py
```

## Step 6: Access the Web Interface
Open your browser and go to:
```
http://localhost:5000
```

## Troubleshooting
- If you get database errors, make sure the `database.db` and `contracts.db` files are not in your `.gitignore` (they should be ignored in the repository but created locally).
- If the tables already exist but have missing columns, you may need to drop and recreate the databases or manually alter the tables.
- Ensure you have write permissions in the project directory.

## Database Schemas
### users table (database.db):
- id (INTEGER PRIMARY KEY)
- username (TEXT UNIQUE NOT NULL)
- password (TEXT NOT NULL)
- private_key (TEXT UNIQUE NOT NULL)
- balance (REAL DEFAULT 100)
- wallet_balance (REAL DEFAULT 0)
- public_key (TEXT)

### contracts table (contracts.db):
- id (INTEGER PRIMARY KEY)
- sender (TEXT)
- recipient (TEXT)
- amount (REAL)
- execution_time (TEXT)
- is_processed (INTEGER DEFAULT 0)
- created_at (DATETIME DEFAULT CURRENT_TIMESTAMP)

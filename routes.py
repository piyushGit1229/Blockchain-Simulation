from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
import sqlite3 
import random
import qrcode
from datetime import datetime
from main import Blockchain
# server_start_time = datetime.now()

app = Flask(__name__)
app.secret_key = 'secretkey'

blockchain = Blockchain(difficulty=3)


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        private_key TEXT UNIQUE NOT NULL
    )
    """)



    
    # Add the 'balance' column if it doesn't exist already
    cursor.execute("PRAGMA table_info(users);")
    columns = cursor.fetchall()


    if not any(column[1] == "balance" for column in columns):
        cursor.execute("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 100;")
        print("Column 'balance' added successfully!")

    conn.commit()
    conn.close()


    



def generate_private_key():
    # Generates a random 5-digit private key
    return str(random.randint(10000, 99999))  # Generates a 5-digit number


@app.route('/')
def intro():
    return render_template('intro.html')


@app.template_filter('datetimeformat')
def datetimeformat(value):
    # Convert UNIX timestamp to readable date format
    return datetime.fromtimestamp(float(value)).strftime('%Y-%m-%d %H:%M:%S')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        private_key = generate_private_key()

        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, private_key) VALUES (?, ?, ?)", 
                (username, password, private_key)
            )
            conn.commit()
            user_id = cursor.lastrowid  # Get the ID of the newly created user
            conn.close()

            # Generate and save the QR code
            qr_path = generate_qr_code(user_id)

            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists. Please try again.", "error")

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username  # Store the username in the session
            session['private_key'] = user[5]  # Store the private key in the session (user[2] is the private_key)
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password. Please try again.", "error")
    return render_template('login.html')


@app.route('/index')
def index():
    username = session.get('username')
    if username:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, private_key FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            user_id = user_data[0]  # Get the user ID
            username = user_data[1]
            private_key = user_data[2]
            qr_path = f"static/qr_codes/{user_id}_qr.png"  # Path to the user's QR code
        else:
            username = "Guest"
            private_key = None
            qr_path = None
    else:
        username = "Guest"
        private_key = None
        qr_path = None

    return render_template('index.html', username=username, private_key=private_key, qr_path=qr_path, blockchain=blockchain)

@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    # Fetching pending transactions
    transactions = blockchain.pending_transactions
    return jsonify(blockchain.pending_transactions)


@app.route('/get_user_transaction', methods=['GET'])
def get_user_transactions():
    username = session.get('username')
    if not username:
        return jsonify({'error': 'User not logged in'}), 401
    
    user_transactions = blockchain.get_user_transactions(username)

    formatted_transactions = [
        {'sender': t['sender'], 'recipient': t['recipient'], 'amount': t['amount'], 'timestamp': t['timestamp']}
        for t in user_transactions
    ]
    return jsonify(formatted_transactions)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    sender = request.form['sender']
    recipient = request.form['recipient']
    amount = float(request.form['amount'])
    sender_private_key = request.form['sender_private_key']

    # Open a connection to the database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    try:
        # Check if the sender exists and fetch their private key and balance
        cursor.execute("SELECT private_key, balance FROM users WHERE username = ?", (sender,))
        sender_data = cursor.fetchone()

        if not sender_data:
            flash("Sender does not exist in the database.", "error")
            return redirect(url_for('index'))

        sender_db_private_key, sender_balance = sender_data

        # Validate the sender's private key
        if sender_private_key != sender_db_private_key:
            flash("Invalid private key for the sender!", "error")
            return redirect(url_for('index'))

        # Check if the sender has sufficient balance
        if sender_balance < amount:
            flash("Insufficient balance to make the transaction!", "error")
            return redirect(url_for('index'))

        # Check if the recipient exists in the database
        cursor.execute("SELECT balance FROM users WHERE username = ?", (recipient,))
        recipient_data = cursor.fetchone()

        if not recipient_data:
            flash("Recipient does not exist in the database.", "error")
            return redirect(url_for('index'))

        # Add the transaction to the blockchain's pending transactions (but do not commit balance changes yet)
        blockchain.add_transaction(sender, recipient, amount)

        flash(f"Transaction of {amount} virtual coins from {sender} to {recipient} was added successfully!", "success")
    except Exception as e:
        flash(f"Transaction failed due to an error: {str(e)}", "error")
    finally:
        conn.close()

    return redirect(url_for('index'))


@app.route('/mine', methods=['POST'])
def mine():
    miner_address = request.form['miner_address']

    # Check if there are any pending contracts to execute before mining
    conn_contracts = sqlite3.connect("contracts.db")
    cursor_contracts = conn_contracts.cursor()

    # Get all contracts that need to be processed
    cursor_contracts.execute("SELECT * FROM contracts WHERE is_processed = 0 AND (execution_time IS NULL OR execution_time <= ?)", 
                              (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
    contracts_to_execute = cursor_contracts.fetchall()

    # Execute all contracts first, but do not commit balances yet
    for contract in contracts_to_execute:
        sender, recipient, amount, execution_time, is_processed = contract
        
        # Check if sender and recipient exist and have enough balance
        conn_users = sqlite3.connect("database.db")
        cursor_users = conn_users.cursor()
        cursor_users.execute("SELECT private_key, balance FROM users WHERE username = ?", (sender,))
        sender_data = cursor_users.fetchone()

        if sender_data:
            sender_balance = sender_data[1]
            if sender_balance >= amount:
                # Add the transaction to the blockchain's pending transactions (not yet processed in database)
                blockchain.add_transaction(sender, recipient, amount)

                # Mark the contract as processed
                cursor_contracts.execute("UPDATE contracts SET is_processed = 1 WHERE sender = ? AND recipient = ? AND amount = ?",
                                          (sender, recipient, amount))
                conn_contracts.commit()
            else:
                flash("Insufficient balance to process contract", "error")
        conn_users.close()

    # Now mine the pending transactions
    blockchain.mine_pending_transactions(miner_address)
    flash("Mining successful! Transactions have been mined.", "success")

    # After mining, now update the database with balances
    conn_users = sqlite3.connect("database.db")
    cursor_users = conn_users.cursor()
    for transaction in blockchain.pending_transactions:
        sender = transaction['sender']
        recipient = transaction['recipient']
        amount = transaction['amount']

        cursor_users.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (amount, sender))
        cursor_users.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, recipient))

    conn_users.commit()
    conn_users.close()

    return redirect(url_for('index'))



@app.route('/get_balance', methods=['POST'])
def get_balance():
    username = session.get('username')
    private_key = session.get('private_key')  # Keep the private key in session
    
    if not username:
        flash("You must log in to view your balance", "error")
        return redirect(url_for('login'))

    # Fetch the balance from the database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance, id FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        balance = user_data[0]  # Extract the balance value
        user_id = user_data[1]  # Extract the user ID for the QR code

        # Generate the QR code path
        qr_path = f"static/qr_codes/{user_id}_qr.png"

        # Ensure the private key and QR code path are passed along with the balance in the template
        return render_template('index.html', blockchain=blockchain, balance=balance, private_key=private_key, qr_path=qr_path)
    else:
        flash("Unable to fetch balance. Please try again later.", "error")
        return redirect(url_for('index'))






@app.route('/check_validity', methods=['GET'])
def check_validity():
    is_valid = blockchain.is_valid()
    return render_template('index.html', blockchain=blockchain, is_valid=is_valid)

@app.route('/signout')
def signout():
    # Clear only user session data (not blockchain data)
    session.pop('username', None)  # Remove the user's session data
    session.pop('private_key', None)  # Remove the user's private key data
    session.modified = True  # Mark session as modified
    
    flash("You have successfully signed out.", "success")  # Flash message for successful logout
    
    return redirect(url_for('login'))  # Redirect to the login page


@app.route('/add_balance/<int:user_id>', methods=['GET', 'POST'])
def add_balance(user_id):
    if request.method == 'POST':
        amount = float(request.form['amount'])

        # Update the user's balance in the database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
        conn.commit()
        conn.close()

        flash(f"Successfully added {amount} virtual coins to your account!", "success")
        return redirect(url_for('index'))

    # Render the Add Balance form
    return render_template('add_balance.html', user_id=user_id)

    
@app.route('/profile')
def profile():
    username = session.get('username')
    if not username:
        flash("You must log in to view your profile", "error")
        return redirect(url_for('login'))
    
    # List of random images to choose from (you can use any set of image URLs)
    profile_images = [
        'https://randomuser.me/api/portraits/men/1.jpg',
        'https://randomuser.me/api/portraits/women/2.jpg',
        'https://randomuser.me/api/portraits/men/3.jpg',
        'https://randomuser.me/api/portraits/women/4.jpg'
    ]
    
    # Select a random image from the list
    profile_image = random.choice(profile_images)
    session['username'] = username
    session['profile_image'] = profile_image
    profile_image = session.get('profile_image')

    return render_template('index.html', username=username, profile_image=profile_image)



def generate_qr_code(user_id):
    # Generate a URL pointing to the add balance page with the user's ID
    qr_url = f"http://127.0.0.1:5000/add_balance/{user_id}"
    qr = qrcode.make(qr_url)
    # Save the QR code as an image file
    qr_path = f"static/qr_codes/{user_id}_qr.png"
    qr.save(qr_path)
    return qr_path



@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('profile_image', None)
    flash("You have been logged out", "info")
    return redirect(url_for('login'))






@app.route('/create_smart_contract', methods=['GET', 'POST'])
def create_smart_contract():
    if request.method == 'POST':
        contract_type = request.form['contract_type']
        sender = request.form['sender']
        recipient = request.form['recipient']
        amount = float(request.form['amount'])
        sender_private_key = request.form['sender_private_key']

        conn_users = sqlite3.connect("database.db")
        cursor_users = conn_users.cursor()

        try:
            # Validate sender in the users table
            cursor_users.execute("SELECT private_key, balance FROM users WHERE username = ?", (sender,))
            sender_data = cursor_users.fetchone()
            if not sender_data or sender_private_key != sender_data[0]:
                flash("Invalid sender or private key!", "error")
                return redirect(url_for('index'))

            cursor_users.execute("SELECT username FROM users WHERE username = ?", (recipient,))
            if not cursor_users.fetchone():
                flash("Recipient does not exist!", "error")
                return redirect(url_for('index'))

            conn_contracts = sqlite3.connect("contracts.db")
            cursor_contracts = conn_contracts.cursor()

            if contract_type == "pay_on_receive":
                # Insert contract into contracts.db for immediate payment when coins are received
                cursor_contracts.execute("""
                    INSERT INTO contracts (sender, recipient, amount, execution_time, is_processed)
                    VALUES (?, ?, ?, NULL, 0)
                """, (sender, recipient, amount))

            elif contract_type == "schedule_payment":
                # Schedule a payment with a future date and time
                execution_time = request.form['execution_time']  # e.g., '2024-12-20 15:00:00'
                cursor_contracts.execute("""
                    INSERT INTO contracts (sender, recipient, amount, execution_time, is_processed)
                    VALUES (?, ?, ?, ?, 0)
                """, (sender, recipient, amount, execution_time))

            conn_contracts.commit()
            flash("Smart contract created successfully!", "success")
            return redirect(url_for('index'))

        except Exception as e:
            conn_users.rollback()
            conn_contracts.rollback()
            flash(f"Error: {str(e)}", "error")
        finally:
            conn_users.close()
            conn_contracts.close()

    return render_template('create_smart_contract.html')



@app.route('/contracts', methods=['GET'])
def contracts():
    # Connect to the contracts database and fetch pending contracts
    conn_contracts = sqlite3.connect("contracts.db")
    cursor_contracts = conn_contracts.cursor()

    # Fetch only pending contracts (is_processed = 0)
    cursor_contracts.execute("""SELECT id, sender, recipient, amount, execution_time, is_processed 
                                FROM contracts
                                WHERE is_processed = 0""")
    contracts = cursor_contracts.fetchall()

    conn_contracts.close()

    # Pass the contracts data to the template
    return render_template('contracts.html', contracts=contracts)


def process_contracts():
    # Establish a connection to the contracts database
    conn_contracts = sqlite3.connect("contracts.db")
    cursor_contracts = conn_contracts.cursor()

    # Get the current date and time
    current_time = datetime.now()

    # Query to get contracts that are not processed yet
    cursor_contracts.execute("SELECT * FROM contracts WHERE is_processed = 0")
    contracts_to_execute = cursor_contracts.fetchall()

    for contract in contracts_to_execute:
        sender, recipient, amount, execution_time, is_processed = contract
        
        # Skip contracts where execution_time is NULL or empty
        if not execution_time:
            continue
        
        # Convert execution_time to datetime object for comparison
        try:
            execution_time = datetime.datetime.strptime(execution_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # If there's an issue in parsing execution_time, skip this contract
            continue
        
        # Check if execution_time is in the future (both date and time)
        if execution_time > current_time:
            continue  # Contract execution time has not arrived yet, skip

        # Proceed with processing the contract if the time has arrived
        conn_users = sqlite3.connect("users.db")
        cursor_users = conn_users.cursor()

        # Fetch sender's balance and validate
        cursor_users.execute("SELECT private_key, balance FROM users WHERE username = ?", (sender,))
        sender_data = cursor_users.fetchone()

        if sender_data:
            sender_balance = sender_data[1]
            if sender_balance >= amount:
                # Deduct amount from sender's balance and add to recipient's balance
                cursor_users.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (amount, sender))
                cursor_users.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, recipient))
                conn_users.commit()

                # Optional: Add the transaction to the blockchain (if setup)
                blockchain.add_transaction(sender, recipient, amount)

                # Flash success message
                flash(f"Transaction of {amount} virtual coins from {sender} to {recipient} was successful!", "success")

                # Mark the contract as processed
                cursor_contracts.execute("UPDATE contracts SET is_processed = 1 WHERE sender = ? AND recipient = ? AND amount = ?",
                                          (sender, recipient, amount))
                conn_contracts.commit()
            else:
                flash("Insufficient balance to process contract", "error")
        
        conn_users.close()

    conn_contracts.close()

# Call the function to process contracts
process_contracts()

@app.route('/get_contracts', methods=['GET'])
def get_contracts():
    conn_contracts = sqlite3.connect("contracts.db")
    cursor_contracts = conn_contracts.cursor()
    cursor_contracts.execute("SELECT id, sender, recipient, amount, execution_time, is_processed FROM contracts")
    contracts = cursor_contracts.fetchall()
    conn_contracts.close()
    
    # Return contracts to be displayed on the frontend
    return jsonify({'contracts': contracts})

# Initialize database and run the app
if __name__ == "__main__":
    init_db()  # Create the database if it doesn't exist
    app.run(debug=True)

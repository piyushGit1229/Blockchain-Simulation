from pymongo import MongoClient
from bson.objectid import ObjectId

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI
db = client['blockchain_db']

# MongoDB collections for users and blockchain data
users_collection = db['users']
blockchain_collection = db['blockchain']

# Add a new user with initial balance
def add_user(username, password, initial_balance=100.0):
    if users_collection.find_one({"username": username}):
        return False  # User already exists
    users_collection.insert_one({"username": username, "password": password, "balance": initial_balance})
    return True

# Get balance of a user
def get_balance(username):
    user = users_collection.find_one({"username": username})
    return user.get("balance", 0.0) if user else 0.0

# Update balance of a user
def update_balance(username, balance):
    users_collection.update_one({"username": username}, {"$set": {"balance": balance}})

# Initialize blockchain (if not already present)
def initialize_blockchain():
    if blockchain_collection.count_documents({}) == 0:
        genesis_block = {
            'index': 0,
            'timestamp': 0,
            'transactions': [],
            'previous_hash': '0',
            'hash': 'genesis_hash'
        }
        blockchain_collection.insert_one({"chain": [genesis_block], "pending_transactions": []})

# Get the current blockchain
def get_blockchain():
    return blockchain_collection.find_one({}) or {"chain": [], "pending_transactions": []}

# Save blockchain to MongoDB
def save_blockchain(chain, pending_transactions):
    blockchain_collection.update_one({}, {"$set": {"chain": chain, "pending_transactions": pending_transactions}})

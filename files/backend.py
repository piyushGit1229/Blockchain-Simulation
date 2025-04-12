from flask import Flask, request, jsonify, render_template
from python import Blockchain  # Import the Blockchain class from python.py

app = Flask(__name__)

# Initialize the Blockchain instance
blockchain = Blockchain(difficulty=3)

# Home route to render the homepage
@app.route('/')
def home():
    return render_template('home.html')

# Endpoint to add a new transaction
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.json
    sender = data.get('sender')
    recipient = data.get('recipient')
    amount = data.get('amount')

    if not sender or not recipient or not amount:
        return jsonify({'message': 'Invalid transaction data'}), 400

    success = blockchain.add_transaction(sender, recipient, float(amount))
    if success:
        return jsonify({'message': 'Transaction added successfully'}), 200
    else:
        return jsonify({'message': 'Transaction failed: Insufficient balance'}), 400

# Endpoint to mine a block
@app.route('/mine_block', methods=['POST'])
def mine_block():
    data = request.json
    miner_address = data.get('miner_address')

    if not miner_address:
        return jsonify({'message': 'Miner address is required'}), 400

    blockchain.mine_pending_transactions(miner_address)
    return jsonify({'message': 'Block mined successfully!', 'chain': get_chain_data()}), 200

# Endpoint to get the blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    return jsonify(get_chain_data()), 200

# Endpoint to get wallet balance
@app.route('/get_balance', methods=['POST'])
def get_balance():
    data = request.json
    address = data.get('address')

    if not address:
        return jsonify({'message': 'Wallet address is required'}), 400

    balance = blockchain.get_balance(address)
    return jsonify({'balance': balance}), 200

# Helper function to convert the blockchain to a serializable format
def get_chain_data():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': block.transaction,
            'previous_hash': block.previous_hash,
            'hash': block.hash,
        })
    return {'chain': chain_data, 'length': len(chain_data)}

if __name__ == '__main__':
    app.run(debug=True)

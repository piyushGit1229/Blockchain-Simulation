import hashlib
import time
import sqlite3
import logging
import json
from threading import Timer

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        logging.info(f"Block mined: {self.hash}")


class Blockchain:
    def __init__(self, difficulty):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.pending_transactions = []
        self.transaction_history = []  # Stores recent mined transactions temporarily
        self.mining_reward = 10

    def create_genesis_block(self):
        return Block(0, "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, recipient, amount):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            # Validate sender and recipient
            cursor.execute("SELECT balance FROM users WHERE username = ?", (sender,))
            sender_balance = cursor.fetchone()

            cursor.execute("SELECT balance FROM users WHERE username = ?", (recipient,))
            recipient_balance = cursor.fetchone()

            if not sender_balance or not recipient_balance:
                logging.warning("Transaction failed: Invalid sender or recipient.")
                return False

            sender_balance = sender_balance[0]

            if sender != "network" and sender_balance < amount:
                logging.warning("Transaction failed: Insufficient balance.")
                return False

            transaction = {
                "sender": sender,
                "recipient": recipient,
                "amount": amount,
                "status": "pending",
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            }

            self.pending_transactions.append(transaction)
            logging.info(f"Transaction added: {transaction}")
            return True

        finally:
            conn.close()

    def mine_pending_transactions(self, miner_address):
        if not self.pending_transactions:
            logging.info("No transactions to mine!")
            return

        # Take all pending transactions
        transactions_to_mine = self.pending_transactions[:]
        self.pending_transactions = []

        # Create and mine a block
        block = Block(len(self.chain), transactions_to_mine, self.get_latest_block().hash)
        block.mine_block(self.difficulty)
        self.chain.append(block)

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            # Process transactions in the mined block
            for transaction in transactions_to_mine:
                self.update_wallet_balance(transaction, cursor)
                transaction["status"] = "success"

                # Add transaction to temporary transaction history
                self.add_to_transaction_history(transaction)

            # Reward the miner
            self.reward_miner(miner_address, cursor)

            conn.commit()
            logging.info(f"Block mined and added to blockchain. Miner {miner_address} rewarded.")

        finally:
            conn.close()

    def update_wallet_balance(self, transaction, cursor):
        sender = transaction["sender"]
        recipient = transaction["recipient"]
        amount = transaction["amount"]

        if sender != "network":
            cursor.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (amount, sender))

        cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, recipient))

    def reward_miner(self, miner_address, cursor):
        cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (self.mining_reward, miner_address))
        logging.info(f"Miner {miner_address} rewarded with {self.mining_reward} coins.")

    def add_to_transaction_history(self, transaction):
        """Add transaction to temporary history and set up its removal after 1 minute."""
        self.transaction_history.append(transaction)
        Timer(60, self.remove_transaction_from_history, args=(transaction,)).start()
        logging.info(f"Transaction added to history: {transaction}")

    def remove_transaction_from_history(self, transaction):
        """Remove transaction from history after 1 minute."""
        if transaction in self.transaction_history:
            self.transaction_history.remove(transaction)
            logging.info(f"Transaction removed from history: {transaction}")

    def get_balance(self, address):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT balance FROM users WHERE username = ?", (address,))
            balance = cursor.fetchone()
            return balance[0] if balance else 0
        finally:
            conn.close()

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                logging.error(f"Invalid hash at block {current_block.index}")
                return False
            if current_block.previous_hash != previous_block.hash:
                logging.error(f"Invalid link at block {current_block.index}")
                return False
        return True

    def display_chain(self):
        if len(self.chain) == 1:
            logging.info("Blockchain contains only the genesis block.")
        for block in self.chain:
            logging.info(f"Block {block.index} - Hash: {block.hash}")
            for transaction in block.transactions:
                logging.info(f"  {transaction['sender']} -> {transaction['recipient']} ({transaction['amount']}) - Status: {transaction['status']}")
            logging.info("-" * 30)

    def display_transaction_history(self):
        logging.info("Recent Transactions (last 1 minute):")
        if not self.transaction_history:
            logging.info("No recent transactions.")
        for transaction in self.transaction_history:
            logging.info(f"  {transaction['sender']} -> {transaction['recipient']} ({transaction['amount']}) - Status: {transaction['status']}")


def main():
    blockchain = Blockchain(difficulty=2)

    while True:
        print("\nBlockchain CLI")
        print("1. Add Transaction")
        print("2. Mine Block")
        print("3. Display Recent Transactions")
        print("4. Check Wallet Balance")
        print("5. Display Blockchain")
        print("6. Check Blockchain Validity")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            sender = input("Sender: ")
            recipient = input("Recipient: ")
            amount = float(input("Amount: "))
            if blockchain.add_transaction(sender, recipient, amount):
                print("Transaction added.")
            else:
                print("Transaction failed.")

        elif choice == "2":
            miner = input("Miner Address: ")
            blockchain.mine_pending_transactions(miner)

        elif choice == "3":
            blockchain.display_transaction_history()

        elif choice == "4":
            address = input("Address: ")
            print(f"Balance: {blockchain.get_balance(address)}")

        elif choice == "5":
            blockchain.display_chain()

        elif choice == "6":
            print("Blockchain valid:", blockchain.is_valid())

        elif choice == "7":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
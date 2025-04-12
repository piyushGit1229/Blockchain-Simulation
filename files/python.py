import hashlib
import time
import json

class Block:
    def __init__(self, index, transaction, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transaction = transaction
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        self.nonce = 0

    # Calculate the hash of the block (SHA256)
    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)  # object to JSON string
        return hashlib.sha256(block_string.encode()).hexdigest()  # unique hash of the string

    # Proof-of-Work: Mine the block
    def mine_block(self, difficulty):
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined: {self.hash}")


class Blockchain:
    def __init__(self, difficulty):
        self.chain = [self.create_genesis_block()]  # Creates a list of blockchains
        self.difficulty = difficulty
        self.pending_transactions = []  # Holds the unconfirmed transactions
        self.mining_reward = 10
        self.wallets = {}  # Holds user wallet balances
        self.initial_balance = 100

    # Create the genesis block
    def create_genesis_block(self):
        return Block(0, "Genesis Block", "0")

    # Get the latest block in the blockchain
    def get_latest_block(self):
        return self.chain[-1]

    # Add a block to the blockchain
    def add_block(self, block):
        self.chain.append(block)

    # Add a transaction to the pending transactions
    def add_transaction(self, sender, recipient, amount):
        # Initialize sender and recipient balances if not already present
        if sender not in self.wallets:
            self.wallets[sender] = self.initial_balance
        if recipient not in self.wallets:
            self.wallets[recipient] = self.initial_balance

        # Check if the sender has enough balance
        if sender != "network" and self.wallets[sender] < amount:
            print("Transaction failed: Insufficient balance.")
            return False

        transaction = {"from": sender, "to": recipient, "amount": amount}
        self.pending_transactions.append(transaction)
        print(f"Transaction added: {transaction}")
        return True

    # Mine a new block and reward the miner
    def mine_pending_transactions(self, miner_address):
        if not self.pending_transactions:
            print("No transactions to mine!")
            return

        block = Block(len(self.chain), self.pending_transactions, self.get_latest_block().hash)
        block.mine_block(self.difficulty)  # Mine the block

        self.chain.append(block)  # Add the mined block to the blockchain

        # Reward the miner
        self.pending_transactions = [{"from": "network", "to": miner_address, "amount": self.mining_reward}]

        # Update the wallets with the transaction information
        for transaction in block.transaction:
            self.update_wallet_balance(transaction)

    # Update the wallet balances based on transactions
    def update_wallet_balance(self, transaction):
        sender = transaction["from"]
        recipient = transaction["to"]
        amount = transaction["amount"]

        if sender != "network":
            self.wallets[sender] = self.wallets.get(sender, 0) - amount
        self.wallets[recipient] = self.wallets.get(recipient, 0) + amount

    # Get the balance of a wallet
    def get_balance(self, address):
        return self.wallets.get(address, 0)

    # Check if the blockchain is valid
    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                print(f"Invalid hash at block {current_block.index}")
                return False
            if current_block.previous_hash != previous_block.hash:
                print(f"Invalid link at block {current_block.index}")
                return False
        return True

    # Display the blockchain
    def display_chain(self):
        for block in self.chain:
            print(f"Block {block.index} - Hash: {block.hash}")
            print(f"Transactions: {block.transaction}")
            print("-" * 30)


# Main function to run the blockchain simulation
def main():
    blockchain = Blockchain(difficulty=3)

    while True:
        print("\nBlockchain CLI")
        print("1. Add Transaction")
        print("2. Mine Block")
        print("3. Check Wallet Balance")
        print("4. Display Blockchain")
        print("5. Check Blockchain Validity")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            sender = input("Enter sender's wallet address: ")
            recipient = input("Enter recipient's wallet address: ")
            amount = float(input("Enter amount: "))
            blockchain.add_transaction(sender, recipient, amount)

        elif choice == "2":
            miner_address = input("Enter miner's wallet address: ")
            blockchain.mine_pending_transactions(miner_address)

        elif choice == "3":
            wallet_address = input("Enter wallet address: ")
            balance = blockchain.get_balance(wallet_address)
            print(f"Wallet Balance: {balance}")

        elif choice == "4":
            blockchain.display_chain()

        elif choice == "5":
            is_valid = blockchain.is_valid()
            print("Blockchain valid:", is_valid)

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

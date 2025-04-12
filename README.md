Blockchain Simulation Project
Welcome to the Blockchain Simulation project! This web application simulates the workings of a blockchain, offering features like adding transactions, mining blocks, checking wallet balances, and validating the blockchain. It also includes a smart contract functionality.

🚀 Features:
Add Transactions: Easily add new transactions to the blockchain.

Mine Blocks: Mine new blocks and add them to the chain.

Check Wallet Balances: Monitor your wallet balance.

Validate Blockchain: Ensure the integrity of the blockchain.

Smart Contracts: Integrate and execute smart contracts.

🛠️ Prerequisites
Before getting started, ensure you have the following installed on your machine:

Python 3.x (latest version recommended)

SQLite (for database management)

Git (for version control)

Required Python Libraries:
To install the necessary Python libraries, run:


pip install -r requirements.txt



📦 Setup Instructions
1. Clone the Repository
Clone the repository to your local machine using:

git clone https://github.com/piyushGit1229/Blockchain-Simulation.git
cd Blockchain-Simulation

2. Set Up the Databases
The project relies on two databases: database.db (for the blockchain) and contracts.db (for smart contracts).

Initialize Databases:
Run the following scripts to automatically create the necessary tables and databases:

Initialize the Main Database (database.db):

python init_db.py

Initialize the Contracts Database (contracts.db):

python init_contracts.py

These scripts will check for existing databases and create new ones if necessary.

3. Running the Application

After the databases are set up, you can launch the application. Start the Flask development server with:

python routes.py

This will run the application locally. Open your browser and go to http://127.0.0.1:5000/ to interact with the blockchain simulation.

4. Interacting with the Blockchain

Once the application is up and running, you can perform the following actions:

Add Transactions: Input transactions to the blockchain.

Mine New Blocks: Mine blocks and add them to the chain.

Check Wallet Balances: View the balance of your wallet.

Validate Blockchain: Confirm the integrity and security of your blockchain.

⚠️ Important Notes
Environment Variables: Always keep your sensitive data (such as API keys or private information) secure. Use a .env file for environment variables.

Database Management: The database files are stored locally. If you need to reset the project, simply delete the database.db and contracts.db files and re-run the initialization scripts.

Testing the Application: You can add more tests by extending the existing test files, ensuring the blockchain remains functional.

📄 License
This project is licensed under the MIT License. See the LICENSE file for more details.
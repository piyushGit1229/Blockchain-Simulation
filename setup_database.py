import subprocess

def run_init_scripts():
    # Run the init_contracts.py script
    subprocess.run(['python', 'init_contracts.py'], check=True)
    
    # Run the init_db.py script
    subprocess.run(['python', 'init_db.py'], check=True)

if __name__ == "__main__":
    run_init_scripts()
    print("Databases initialized successfully.")

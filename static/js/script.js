// Fetch and display contracts on page load
window.onload = function() {
    fetchContracts();
};

// Fetch contracts from the backend
function fetchContracts() {
    fetch('/get_contracts')
        .then(response => response.json())
        .then(data => {
            const contracts = data.contracts;
            const contractsContainer = document.getElementById("contracts-container");
            contractsContainer.innerHTML = ''; // Clear the container first

            contracts.forEach(contract => {
                const { id, sender, recipient, amount, execution_time, is_processed } = contract;

                // Check if the contract is processed or still pending
                const contractStatus = is_processed === 1 ? "Processed" : "Pending";
                const contractDiv = document.createElement('div');
                contractDiv.classList.add('contract');
                contractDiv.innerHTML = `
                    <p><strong>Sender:</strong> ${sender}</p>
                    <p><strong>Recipient:</strong> ${recipient}</p>
                    <p><strong>Amount:</strong> $${amount}</p>
                    <p><strong>Execution Time:</strong> ${execution_time}</p>
                    <p>Status: <span id="status-${id}">${contractStatus}</span></p>
                `;

                contractsContainer.appendChild(contractDiv);

                // Check if the contract's execution time has passed and update the status
                const executionTime = new Date(execution_time);
                const now = new Date();

                if (executionTime <= now && is_processed === 0) {
                    setTimeout(() => {
                        // Mark as processed in the UI and show success message
                        document.getElementById(`status-${id}`).innerText = "Processed";
                        showFlashMessage(recipient, amount);
                    }, 1000); // 1 second delay before showing the flash message
                }
            });
        })
        .catch(error => {
            console.error("Error fetching contracts:", error);
        });
}

// Show a success flash message
function showFlashMessage(recipient, amount) {
    const flashMessage = document.getElementById("flashMessage");
    flashMessage.classList.remove("hidden");
    flashMessage.innerText = `${recipient} has received $${amount} via smart contract successfully!`;
    
    // Hide the message after 5 seconds
    setTimeout(() => {
        flashMessage.classList.add("hidden");
    }, 5000);
}

window.onload = function() {
    // Check for a success flag in the URL (you could also use Flask to pass this in the template)
    const flashMessage = document.getElementById("flashMessage");

    // Example of triggering the flash message
    // This could be triggered when a payment is successfully processed
    if (window.location.search.includes("success=true")) {
        flashMessage.textContent = "Payment successfully received!";
        flashMessage.classList.remove("hidden");
        flashMessage.classList.add("show");
        setTimeout(() => flashMessage.classList.add("hidden"), 3000);
    }
};

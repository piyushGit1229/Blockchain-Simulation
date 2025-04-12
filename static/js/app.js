
fetch('/get_transactions')
.then(response => response.json())
.then(data => {
    const transactionList = document.getElementById('transactionList');
    // Clear the current transaction list
    transactionList.innerHTML = '';
    // Add each transaction to the list
    data.forEach(transaction => {
        const li = document.createElement('li');
        
        // Show the status (success or pending) along with the transaction details
        const status = transaction.status ? transaction.status : 'pending';  // Default to pending if status is not available
        li.textContent = `${transaction.timestamp} - ${transaction.sender} sent ${transaction.amount} to ${transaction.recipient} - Status: ${status}`;
        
        transactionList.appendChild(li);
    });
})
.catch(error => {
    console.error('Error fetching recent transactions:', error);
});

const userIcon = document.getElementById("userIcon");
const walletModal = document.getElementById("walletModal");
const closeBtn = document.getElementById("closeBtn");
const transactionList2 = document.getElementById("transactionList2");

const currentUserId = document.getElementById('app').getAttribute('data-username');

// Store successful transactions globally to persist them
let personalTransactions = [];

userIcon.addEventListener('click', showWallet);
closeBtn.addEventListener('click', closeWallet);

function showWallet() {
    if (personalTransactions.length === 0) {
        fetchTransactions();  // Fetch and display transactions if not already fetched
    } else {
        updatePersonalTransactionTracker(personalTransactions);  // Use cached successful transactions
    }
    walletModal.style.display = 'flex';
}

function fetchTransactions() {
    fetch('/get_transactions')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch transactions');
            }
            return response.json();
        })
        .then(data => {
            // Filter the successful transactions related to the current user
            const userTransactions = data.filter(transaction => {
                return (transaction.sender === currentUserId || transaction.recipient === currentUserId) && transaction.status === 'success';
            });

            // Update global personal transactions
            personalTransactions = userTransactions;

            updatePersonalTransactionTracker(userTransactions);  // Display them
        })
        .catch(error => {
            console.error('Error fetching transactions:', error);
        });
}

function updatePersonalTransactionTracker(transactions) {
    // Clear the existing transaction list
    transactionList2.innerHTML = '';
    
    // Add each successful transaction to the list
    transactions.forEach(transaction => {
        const li = document.createElement('li');
        li.textContent = `${transaction.timestamp} - ${transaction.sender} sent ${transaction.amount} to ${transaction.recipient} - Status: ${transaction.status}`;
        transactionList2.appendChild(li);
    });
}

// Simulating successful mining of a block (for demo purposes)
function onBlockMined(transactionId) {
    // Update the transaction status to 'success' for the mined transaction
    const updatedTransactions = personalTransactions.map(transaction => {
        if (transaction.id === transactionId) {
            transaction.status = 'success';  // Mark the transaction as successful
        }
        return transaction;
    });

    // Update the global personal transactions
    personalTransactions = updatedTransactions;

    // Update the UI to reflect the new status
    updatePersonalTransactionTracker(updatedTransactions);
}

function closeWallet() {
    walletModal.style.display = 'none';
}

document.getElementById('showTransactionsBtn').addEventListener('click', function() {
    if (personalTransactions.length === 0) {
        fetchTransactions();  // Fetch transactions if none exist in the cache
    } else {
        updatePersonalTransactionTracker(personalTransactions);  // Use cached transactions
    }
    walletModal.style.display = 'block';
});
// Select the elements
const showTransactionsBtn = document.getElementById('showTransactionsBtn');
const qrCodeContainer = document.getElementById('qrCodeContainer');
const closeQRCodeBtn = document.getElementById('closeQRCodeBtn');
const mainContent = document.getElementById('mainContent'); // Assuming all the main content is inside an element with id "mainContent"

// Handle click event on "Add Money to Wallet" button
showTransactionsBtn.addEventListener('click', function() {
    // Show the QR code with a fade-in effect
    qrCodeContainer.style.display = 'flex';  // Make the QR code container visible and center it
    setTimeout(function() {
        qrCodeContainer.style.opacity = 1;  // Fade in the QR code
    }, 10);  // Small timeout to trigger the transition effect

    // Apply background blur to the main content
    mainContent.style.filter = 'blur(50px)';
});

// Handle close button click event
closeQRCodeBtn.addEventListener('click', function() {
    // Hide the QR code with a fade-out effect
    qrCodeContainer.style.opacity = 0;  // Fade out the QR code
    setTimeout(function() {
        qrCodeContainer.style.display = 'none';  // Hide the QR code container after the fade-out
    }, 300);  // Wait for the fade-out transition to complete (300ms)

    // Remove background blur
    mainContent.style.filter = 'none';
});


// Get elements
const hoverTrigger = document.querySelector('.hover-trigger');
const infoPopup = document.querySelector('.info-popup');
const popupContent = document.querySelector('.popup-content');

// Ensure the popup is initially hidden
infoPopup.style.display = 'none';

// Show popup on click of Smart Contract text
hoverTrigger.addEventListener('click', () => {
    infoPopup.style.display = 'flex';
});

// Hide popup if the user clicks outside the popup content
window.addEventListener('click', (e) => {
    if (!popupContent.contains(e.target) && !hoverTrigger.contains(e.target)) {
        infoPopup.style.display = 'none';
    }
});

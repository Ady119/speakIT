
document.addEventListener("DOMContentLoaded", function() {
const cards = document.querySelectorAll('.card');
const currentCardElem = document.getElementById('currentCard');
const totalCardsElem = document.getElementById('totalCards');
const prevButton = document.getElementById('prevCard');
const nextButton = document.getElementById('nextCard');
const progress = document.getElementById('progress');
const resetButton = document.getElementById('resetProgress'); // Reference to the reset button

let currentCardNumber = 0; // Start from 0 to show 0/1 initially
let lastVisitedCardNumber = 0; // Track the last visited card separately

// Load saved progress if available
const savedProgress = localStorage.getItem('currentCardNumber_${lessonId}');
const savedLastVisitedCardNumber = localStorage.getItem('lastVisitedCardNumber');

if (savedProgress) {
    currentCardNumber = parseInt(savedProgress, 10);
    lastVisitedCardNumber = savedLastVisitedCardNumber ? parseInt(savedLastVisitedCardNumber, 10) : currentCardNumber; // Initialize lastVisitedCardNumber
}

function updateCardDisplay() {
    // Hide all cards
    cards.forEach(card => card.style.display = 'none');

    // Update current card number display
    currentCardElem.textContent = currentCardNumber + 1; // Display current card number starting from 1

    // Show the current card
    cards[currentCardNumber].style.display = 'block';

    // Update progress bar based on lastVisitedCardNumber
    const percentage = (lastVisitedCardNumber / (cards.length - 1)) * 100;
    progress.style.width = Math.floor(percentage) + '%';
    progress.innerText = progress.style.width;

    // Save current card number and lastVisitedCardNumber to localStorage
    localStorage.setItem('currentCardNumber_${lessonId}', currentCardNumber);
    localStorage.setItem('lastVisitedCardNumber', lastVisitedCardNumber);
}

prevButton.addEventListener('click', function () {
    if (currentCardNumber > 0) {
        currentCardNumber--;
        if (currentCardNumber > lastVisitedCardNumber) {
            lastVisitedCardNumber = currentCardNumber; // Update lastVisitedCardNumber
        }
        updateCardDisplay();
    }
});

nextButton.addEventListener('click', function () {
    if (currentCardNumber < cards.length - 1) {
        currentCardNumber++;
        if (currentCardNumber > lastVisitedCardNumber) {
            lastVisitedCardNumber = currentCardNumber; // Update lastVisitedCardNumber
        }
        updateCardDisplay();
    }
});

// Add an event listener to reset progress when the reset button is clicked
resetButton.addEventListener('click', function () {
    localStorage.removeItem('currentCardNumber');
    localStorage.removeItem('lastVisitedCardNumber'); // Remove lastVisitedCardNumber as well
    currentCardNumber = 0; // Reset to the first card
    lastVisitedCardNumber = 0; // Reset lastVisitedCardNumber
    updateCardDisplay(); // Update the display after resetting progress
});

// Add an event listener to save progress when the user leaves the page
window.addEventListener('beforeunload', function () {
// Calculate the user's progress based on the last visited card number
const totalCards = cards.length;

// Round up the progress percentage based on lastVisitedCardNumber
const roundedProgress = Math.floor((lastVisitedCardNumber / (cards.length - 1)) * 100);

// Send a progress update to the server when the user leaves the page
const lessonId = '{{ lesson_id }}'; // Replace with your lesson ID from the template
const userId = '{{ user_id }}'; // Replace with your user ID or implement authentication logic
const progressData = {
user_id: userId,
lesson_id: lessonId,
progress: roundedProgress
};

fetch('/update_progress', {
method: 'POST',
headers: {
    'Content-Type': 'application/json'
},
body: JSON.stringify(progressData)
})
.then(response => {
    if (response.ok) {
        console.log('Progress saved successfully');
    } else {
        console.error('Failed to save progress');
    }
});
});

    // Initial setup
    totalCardsElem.textContent = cards.length;
    updateCardDisplay();
});

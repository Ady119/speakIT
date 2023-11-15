window.onload = function() {
    var flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
        }, 2000); // Starts the fade out after 5 seconds

        // Wait for the transition to end before setting display: none
        message.addEventListener('transitionend', function() {
            message.style.display = 'none';
        });
    });
};

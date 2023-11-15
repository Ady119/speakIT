    window.addEventListener('beforeunload', function (e) {
    e.preventDefault(); // Prevent the default action
    e.returnValue = 'Are you sure you want to leave this page'; // Required for Chrome compatibility
    return 'Are you sure you want to leave this page?';
});

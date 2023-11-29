document.getElementById('see_password').addEventListener('click', function (e) {
    // Grab the password field
    var password_input = document.getElementById('password');


    if (this.checked) {
        password_input.type = 'text';
    } else {
        password_input.type = 'password';
    }
});

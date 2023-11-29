    document.addEventListener("DOMContentLoaded", function() {
        const progressBars = document.querySelectorAll('.progress-bar-container-2');

        progressBars.forEach(progressBar => {
            const progress = parseInt(progressBar.getAttribute('data-progress'));
            if (progress > 0) {
                progressBar.classList.add('progress-2'); // Add the class to style with green color
                progressBar.style.width = `${progress}%`; // Set the progress width
            }
        });
    });


    //my learning content page

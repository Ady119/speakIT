document.addEventListener("DOMContentLoaded", function () {
    // Get all audio elements
    var audios = document.querySelectorAll("audio");

    audios.forEach(function (audio) {
        var playButton = audio.nextElementSibling; // Get the next sibling (play button)
        playButton.addEventListener("click", function () {
            if (audio.paused) {
                audio.play();
                playIcon.classList.remove("fa-play");
                playIcon.classList.add("fa-pause");
            } else {
                audio.pause();
                audio.currentTime = 0; // Reset audio playback to the beginning
                playIcon.classList.remove("fa-pause");
                playIcon.classList.add("fa-play");
            }
        });

        audio.addEventListener("ended", function () {
            audio.currentTime = 0;  // Reset the audio playback to the beginning
            playIcon.classList.remove("fa-pause");
            playIcon.classList.add("fa-play");
        });
    });
});

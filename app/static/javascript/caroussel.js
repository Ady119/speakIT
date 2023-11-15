let slideIndex = 0;
const slides = document.querySelectorAll(".slide");
const totalSlides = slides.length;

document.querySelector(".prev").addEventListener("click", () => {
moveSlide(-1);
});

document.querySelector(".next").addEventListener("click", () => {
moveSlide(1);
});

function moveSlide(step) {
slideIndex = (slideIndex + step + totalSlides) % totalSlides;
updateSlidePosition();
}

function updateSlidePosition() {
const offset = -slideIndex * 100;
for (let i = 0; i < slides.length; i++) {
  slides[i].style.transform = `translateX(${offset}%)`;
}
}

// Automatic slide change every 3 seconds
setInterval(() => {
moveSlide(1);
}, 5000);

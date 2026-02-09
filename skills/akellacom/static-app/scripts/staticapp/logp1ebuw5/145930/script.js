document.addEventListener("DOMContentLoaded", function () {
    const noBtn = document.getElementById("noBtn");

    noBtn.style.position = "absolute"; // Ensures button is movable
    noBtn.style.transition = "left 0.4s ease, top 0.4s ease"; // Smooth transition

    noBtn.addEventListener("mouseover", function () {
        const x = Math.random() * (window.innerWidth - noBtn.offsetWidth);
        const y = Math.random() * (window.innerHeight - noBtn.offsetHeight);
        
        noBtn.style.left = `${x}px`;
        noBtn.style.top = `${y}px`;
    });
});

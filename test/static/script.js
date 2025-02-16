document.addEventListener("DOMContentLoaded", function() {
    let cards = document.querySelectorAll('.card');
    let middle = Math.floor(cards.length / 2);
    let screenWidth = window.innerWidth;
    
    // Adaptive spacing based on screen width
    let maxOffset = 100; // Maximum spacing for large screens
    let minOffset = 50;  // Minimum spacing for small screens
    let offset = Math.max(minOffset, Math.min(maxOffset, screenWidth / (cards.length * 1.5)));

    cards.forEach((card, index) => {
        let position = (index - middle) * offset;
        card.style.left = `calc(50% + ${position}px)`;
    });
});

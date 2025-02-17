// Wait for the DOM to fully load before executing the script
document.addEventListener("DOMContentLoaded", function() {
    // Select all elements with the class 'card'
    let cards = document.querySelectorAll('.card');
    // Calculate the middle index of the cards array
    let middle = Math.floor(cards.length / 2);
    // Get the current width of the window
    let screenWidth = window.innerWidth;
    
    // Define the maximum and minimum spacing for the cards
    let maxOffset = 100; // Maximum spacing for large screens
    let minOffset = 50;  // Minimum spacing for small screens
    // Calculate the offset based on the screen width and number of cards
    let offset = Math.max(minOffset, Math.min(maxOffset, screenWidth / (cards.length * 1.5)));

    // Loop through each card and set its position
    cards.forEach((card, index) => {
        // Calculate the position of the card relative to the middle
        let position = (index - middle) * offset;
        // Set the left position of the card using CSS
        card.style.left = `calc(50% + ${position}px)`;
    });

    // Select all elements with the class 'dcard'
    let dcards = document.querySelectorAll('.dcard');

    // Loop through each dcard and set its position
    dcards.forEach((dcard, index) => {
        // Set the top position of the dcard using CSS
        dcard.style.top = `${index * 0}px`; // Adjust the 5px value as needed for spacing
    });
});

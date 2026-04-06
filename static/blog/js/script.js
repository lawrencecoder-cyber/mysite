// Simple interaction example

document.addEventListener("DOMContentLoaded", () => {
    console.log("Blog loaded successfully");

    // Example: highlight clicked post
    const cards = document.querySelectorAll(".post-card");

    cards.forEach(card => {
        card.addEventListener("click", () => {
            card.style.border = "2px solid #00bcd4";
        });
    });
});

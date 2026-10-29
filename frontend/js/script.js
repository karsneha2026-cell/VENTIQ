
/* ========================================
   VENTIQ — Homepage Functionality
======================================== */

document.addEventListener("DOMContentLoaded", () => {
    const searchForm = document.getElementById("searchForm");
    const searchInput = document.getElementById("eventSearch");
    const categoryButtons = document.querySelectorAll(".category-card");
    const eventCards = document.querySelectorAll(".event-card");
    const noResults = document.getElementById("noResults");

    let selectedCategory = "All";

    // Filter events by search text and category
    function filterEvents() {
        const searchText = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        eventCards.forEach((card) => {
            const title = card.dataset.title.toLowerCase();
            const category = card.dataset.category.toLowerCase();
            const cardText = card.textContent.toLowerCase();

            const matchesSearch =
                title.includes(searchText) ||
                category.includes(searchText) ||
                cardText.includes(searchText);

            const matchesCategory =
                selectedCategory === "All" ||
                card.dataset.category === selectedCategory;

            const shouldShow = matchesSearch && matchesCategory;

            card.hidden = !shouldShow;

            if (shouldShow) {
                visibleCount++;
            }
        });

        noResults.hidden = visibleCount !== 0;
    }

    // Search events
    searchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        filterEvents();

        document.getElementById("events").scrollIntoView({
            behavior: "smooth"
        });
    });

    // Filter while typing
    searchInput.addEventListener("input", filterEvents);

    // Select an event category
    categoryButtons.forEach((button) => {
        button.addEventListener("click", () => {
            selectedCategory = button.dataset.category;

            categoryButtons.forEach((categoryButton) => {
                categoryButton.classList.remove("active");
            });

            button.classList.add("active");
            filterEvents();

            document.getElementById("events").scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        });
    });

    console.log("VENTIQ homepage initialized successfully!");
});

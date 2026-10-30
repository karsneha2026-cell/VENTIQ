
/* ========================================
   VENTIQ — Admin Dashboard
   Connected to Flask + SQLite
======================================== */

document.addEventListener("DOMContentLoaded", () => {
    const addEventBtn = document.getElementById("addEventBtn");
    const cancelEventBtn = document.getElementById("cancelEventBtn");
    const formContainer = document.getElementById("eventFormContainer");
    const eventForm = document.getElementById("adminEventForm");
    const eventList = document.getElementById("adminEventList");

    const API_URL = "https://ventiq-2qjv.onrender.com/api/events";
    const STATS_URL = "https://ventiq-2qjv.onrender.com/api/stats";
    async function loadStats() {
    try {
        const response = await fetch(STATS_URL);

        if (!response.ok) {
            throw new Error("Could not load dashboard statistics.");
        }

        const stats = await response.json();

        document.getElementById("totalEvents").textContent =
            stats.total_events;

        document.getElementById("totalBookings").textContent =
            stats.total_bookings;

        document.getElementById("totalUsers").textContent =
            stats.total_users;

        document.getElementById("totalRevenue").textContent =
            `₹${stats.total_revenue}`;
    } catch (error) {
        console.error("Dashboard statistics error:", error);
    }
 }
    async function loadEvents() {
        eventList.replaceChildren();

        try {
            const response = await fetch(API_URL);

            if (!response.ok) {
                throw new Error("Could not load events.");
            }

            const events = await response.json();

            document.getElementById("totalEvents").textContent =
                events.length;

            if (events.length === 0) {
                const row = document.createElement("tr");
                const cell = document.createElement("td");

                cell.colSpan = 5;
                cell.textContent = "No events found.";
                row.appendChild(cell);
                eventList.appendChild(row);
                return;
            }

            events.forEach((event) => {
                const row = document.createElement("tr");

                [
                    event.title,
                    event.category,
                    event.event_date,
                    event.location,
                    `₹${event.price}`
                ].forEach((value) => {
                    const cell = document.createElement("td");
                    cell.textContent = value;
                    row.appendChild(cell);
                });

                eventList.appendChild(row);
            });
        } catch (error) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 5;
            cell.textContent =
                "Unable to load events. Make sure the Flask server is running.";

            row.appendChild(cell);
            eventList.appendChild(row);

            console.error(error);
        }
    }

    addEventBtn.addEventListener("click", () => {
        formContainer.hidden = false;
        document.getElementById("eventTitle").focus();
    });

    cancelEventBtn.addEventListener("click", () => {
        formContainer.hidden = true;
        eventForm.reset();
    });

    eventForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const newEvent = {
            title: document.getElementById("eventTitle").value.trim(),
            category: document.getElementById("eventCategory").value,
            event_date: document.getElementById("eventDate").value,
            location: document.getElementById("eventLocation").value.trim(),
            price: Number(document.getElementById("eventPrice").value)
        };

        if (
            !newEvent.title ||
            !newEvent.category ||
            !newEvent.event_date ||
            !newEvent.location ||
            !Number.isFinite(newEvent.price) ||
            newEvent.price < 0
        ) {
            alert("Please enter valid event details.");
            return;
        }

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(newEvent)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "Could not save event.");
            }

            alert("Event saved to the database successfully!");

            eventForm.reset();
            formContainer.hidden = true;

            await loadEvents();
        } catch (error) {
            alert(
                "Could not save event. Check that Flask is running, " +
                "then try again."
            );
            console.error(error);
        }
    });

    loadEvents();
    loadStats();
});

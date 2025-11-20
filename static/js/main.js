// ---------------------------------------------------------
// main.js — Global UI Enhancements for Timeless Threads
// ---------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    // ======================================================
    // 1. AUTO-HIDE FLASH MESSAGES (after 5 seconds)
    //
    // Bootstrap alerts displayed via Flask flash messages
    // fade out automatically for smoother UX.
    //
    // - Adds fade-out class
    // - Then closes the alert using Bootstrap JS
    // ======================================================
    const flashMessages = document.querySelectorAll(".alert");
    if (flashMessages.length) {
        setTimeout(() => {
            flashMessages.forEach(msg => {
                msg.classList.add("fade-out");
                setTimeout(() => {
                    try {
                        bootstrap.Alert.getOrCreateInstance(msg).close();
                    } catch (err) {
                        // Bootstrap might not be loaded or alert already removed
                    }
                }, 400);
            });
        }, 5000);
    }

    // ======================================================
    // 2. SMOOTH SCROLL FOR ANCHOR LINKS (#target)
    //
    // Any <a href="#section"> smoothly scrolls to that element.
    // Makes in-page navigation more elegant.
    // ======================================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (e) {
            const target = document.querySelector(this.getAttribute("href"));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: "smooth" });
            }
        });
    });

    // ======================================================
    // 3. "SCROLL TO TOP" BUTTON
    //
    // Button appears when the user scrolls down 300px.
    // On click, smoothly scrolls back to top.
    // ======================================================
    const scrollBtn = document.getElementById("scrollTopBtn");
    if (scrollBtn) {
        window.addEventListener("scroll", () => {
            scrollBtn.style.display = window.scrollY > 300 ? "block" : "none";
        });

        scrollBtn.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // ======================================================
    // 4. PINCODE CHECKER (Delivery Availability)
    //
    // Users enter a 6-digit PIN code → API request is made to
    // https://api.postalpincode.in/pincode/<PIN>
    //
    // Displays:
    //   - Delivery availability
    //   - District & State
    //   - Estimated delivery days (based on zones)
    // ======================================================
    const btn = document.getElementById("checkPincodeBtn");
    const input = document.getElementById("pincodeInput");
    const result = document.getElementById("pincodeResult");

    if (btn && input && result) {
        btn.addEventListener("click", async () => {
            const pincode = input.value.trim();

            // Validate PIN format
            if (pincode.length !== 6) {
                result.innerHTML = `<div class="text-danger">Enter a valid 6-digit PIN code.</div>`;
                return;
            }

            result.innerHTML = `<div class="text-info">Checking availability...</div>`;

            try {
                // Fetch postal data
                const res = await fetch(`https://api.postalpincode.in/pincode/${pincode}`);
                const data = await res.json();

                if (data[0].Status !== "Success") {
                    result.innerHTML = `<div class="text-danger">Delivery not available for this location.</div>`;
                    return;
                }

                // Extract location info
                const district = data[0].PostOffice[0].District;
                const state = data[0].PostOffice[0].State;

                const deliveryDays = getDeliveryDays(state);

                // Success message
                result.innerHTML = `
                    <div class="alert alert-success">
                        ✔ Delivery available to <b>${district}, ${state}</b><br>
                        🚚 Estimated Delivery: <b>${deliveryDays} days</b>
                    </div>
                `;
            } catch (err) {
                result.innerHTML = `<div class="text-danger">Error checking delivery.</div>`;
            }
        });
    }

    // Zone-based delivery estimate helper
    function getDeliveryDays(state) {
        const north = ["Delhi", "Haryana", "Punjab", "UP", "Himachal Pradesh"];
        const south = ["Karnataka", "Tamil Nadu", "Kerala", "Telangana"];
        const west  = ["Maharashtra", "Gujarat", "Rajasthan"];
        const east  = ["West Bengal", "Odisha", "Assam", "Bihar"];

        if (north.includes(state)) return 3;
        if (south.includes(state)) return 5;
        if (west.includes(state)) return 4;
        if (east.includes(state)) return 6;
        return 7; // fallback for remote regions
    }

    // ======================================================
    // 5. FADE-IN EFFECT FOR PRODUCT & CATEGORY CARDS
    //
    // # Improves page aesthetics by animating cards on load.
    // ======================================================
    document.querySelectorAll(".product-card, .category-card")
        .forEach(card => card.classList.add("fade-in"));

    // ======================================================
    // 6. CATEGORY + PRODUCT CARD SLIDESHOW
    //
    // Each product/category card switches through its images
    // on hover (auto slideshow). Also supports manual prev/next.
    //
    // - Images defined via data-images="[...]"
    // - Smooth fade animation
    // - Auto-rotate with random timing
    // ======================================================
    document.querySelectorAll(".product-img-container").forEach(container => {

        const images = JSON.parse(container.dataset.images);
        const img = container.querySelector(".product-img-slide");
        const prev = container.querySelector(".prod-prev");
        const next = container.querySelector(".prod-next");

        let index = 0;
        let interval = null;

        // Smooth fade transition effect
        function swapImage(src) {
            img.classList.add("fade-out");
            setTimeout(() => {
                img.src = src;
                img.classList.remove("fade-out");
            }, 200);
        }

        function nextImage() {
            index = (index + 1) % images.length;
            swapImage(images[index]);
        }

        function prevImage() {
            index = (index - 1 + images.length) % images.length;
            swapImage(images[index]);
        }

        function resetImage() {
            index = 0;
            swapImage(images[0]);
        }

        function startAuto() {
            stopAuto();
            interval = setInterval(nextImage, 1200 + Math.random() * 1500);
        }

        function stopAuto() {
            if (interval) clearInterval(interval);
            interval = null;
        }

        // Start/stop slideshow on hover
        container.addEventListener("mouseenter", startAuto);
        container.addEventListener("mouseleave", () => {
            stopAuto();
            resetImage();
        });

        // Manual navigation
        next.addEventListener("click", e => {
            e.preventDefault();
            e.stopPropagation();
            stopAuto();
            nextImage();
        });

        prev.addEventListener("click", e => {
            e.preventDefault();
            e.stopPropagation();
            stopAuto();
            prevImage();
        });
    });

}); // END first DOMContentLoaded



// ==========================================================
// PRODUCT DETAIL PAGE — MAIN IMAGE SLIDER
//
// Similar to card slideshow but dedicated to product detail.
// Includes:
//   - Auto rotation
//   - Manual next/prev
//   - Thumbnail click selection
//   - Fade animation
// ==========================================================

document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".pd-main-img-container").forEach(container => {

        const images = JSON.parse(container.dataset.images);
        const img = container.querySelector(".pd-main-img");
        const prev = container.querySelector(".pd-prev");
        const next = container.querySelector(".pd-next");
        const thumbs = container.parentElement.querySelectorAll(".pd-thumb");

        let index = 0;
        let interval = null;

        // Updates main image + active thumbnail
        function update() {
            img.style.opacity = 0;
            setTimeout(() => {
                img.src = images[index];
                img.style.opacity = 1;
            }, 200);

            thumbs.forEach(t => t.classList.remove("active"));
            if (thumbs[index]) thumbs[index].classList.add("active");
        }

        function startAuto() {
            stopAuto();
            interval = setInterval(() => {
                index = (index + 1) % images.length;
                update();
            }, 2200);
        }

        function stopAuto() {
            if (interval) clearInterval(interval);
            interval = null;
        }

        // Manual next/prev controls
        next.addEventListener("click", e => {
            e.preventDefault();
            e.stopPropagation();
            index = (index + 1) % images.length;
            update();
            stopAuto();
        });

        prev.addEventListener("click", e => {
            e.preventDefault();
            e.stopPropagation();
            index = (index - 1 + images.length) % images.length;
            update();
            stopAuto();
        });

        // Thumbnail click -> jump to image
        thumbs.forEach((t, i) => {
            t.addEventListener("click", () => {
                index = i;
                update();
                stopAuto();
            });
        });

        container.addEventListener("mouseenter", stopAuto);
        container.addEventListener("mouseleave", startAuto);

        startAuto();
    });

});


// ======================================================
// SIZE & COLOR SELECTORS (Product Detail Page UI)
// ======================================================

// SIZE BUTTONS — highlight selected size and store hidden input
document.querySelectorAll(".pd-size-option")?.forEach(btn => {
    btn.addEventListener("click", () => {

        // Remove active from all buttons
        document.querySelectorAll(".pd-size-option")
            .forEach(el => el.classList.remove("active"));

        // Activate the clicked option
        btn.classList.add("active");

        // Store selected size in hidden input for form submission
        document.getElementById("selectedSize").value = btn.dataset.size;
    });
});

// COLOR BUTTONS — highlight selected color and store hidden input
document.querySelectorAll(".pd-color-option")?.forEach(c => {
    c.addEventListener("click", () => {

        // Remove active from all color buttons
        document.querySelectorAll(".pd-color-option")
            .forEach(el => el.classList.remove("active"));

        // Activate the clicked option
        c.classList.add("active");

        // Store selected color in hidden input
        document.getElementById("selectedColor").value = c.dataset.color;
    });
});

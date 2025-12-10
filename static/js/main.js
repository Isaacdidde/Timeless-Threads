// ======================================================================
// main.js – Production-Ready Frontend Enhancements for Timeless Threads
// ======================================================================

document.addEventListener("DOMContentLoaded", () => {

    // ======================================================
    // UTILITIES
    // ======================================================

    const fadeOut = (el, duration = 200) => {
        if (!el) return;
        el.classList.add("fade-out");
        return new Promise(resolve => setTimeout(resolve, duration));
    };

    const smoothUpdateImage = (imgEl, src, duration = 200) => {
        if (!imgEl) return;
        imgEl.style.opacity = 0;
        setTimeout(() => {
            imgEl.src = src;
            imgEl.style.opacity = 1;
        }, duration);
    };


    // ======================================================
    // 1. AUTO-HIDE FLASH MESSAGES
    // ======================================================
    (() => {
        const alerts = document.querySelectorAll(".alert");
        if (!alerts.length) return;

        setTimeout(() => {
            alerts.forEach(async alert => {
                await fadeOut(alert, 350);
                try {
                    bootstrap.Alert.getOrCreateInstance(alert).close();
                } catch (_) {}
            });
        }, 5000);
    })();


    // ======================================================
    // 2. SMOOTH SCROLL FOR IN-PAGE LINKS
    // ======================================================
    (() => {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener("click", e => {
                const target = document.querySelector(anchor.getAttribute("href"));
                if (!target) return;
                e.preventDefault();
                target.scrollIntoView({ behavior: "smooth" });
            });
        });
    })();


    // ======================================================
    // 3. SCROLL-TO-TOP BUTTON
    // ======================================================
    (() => {
        const btn = document.getElementById("scrollTopBtn");
        if (!btn) return;

        window.addEventListener("scroll", () => {
            btn.style.display = window.scrollY > 300 ? "block" : "none";
        });

        btn.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    })();


    // ======================================================
    // 4. PINCODE DELIVERY CHECKER
    // ======================================================
    (() => {
        const btn = document.getElementById("checkPincodeBtn");
        const input = document.getElementById("pincodeInput");
        const output = document.getElementById("pincodeResult");

        if (!btn || !input || !output) return;

        const zones = {
            north: ["Delhi", "Haryana", "Punjab", "UP", "Himachal Pradesh"],
            south: ["Karnataka", "Tamil Nadu", "Kerala", "Telangana"],
            west: ["Maharashtra", "Gujarat", "Rajasthan"],
            east: ["West Bengal", "Odisha", "Assam", "Bihar"]
        };

        const estimateDays = (state) => {
            if (zones.north.includes(state)) return 3;
            if (zones.south.includes(state)) return 5;
            if (zones.west.includes(state)) return 4;
            if (zones.east.includes(state)) return 6;
            return 7;
        };

        btn.addEventListener("click", async () => {
            const pin = input.value.trim();

            if (pin.length !== 6) {
                output.innerHTML = `<div class="text-danger">Enter a valid 6-digit PIN code.</div>`;
                return;
            }

            output.innerHTML = `<div class="text-info">Checking availability...</div>`;

            try {
                const res = await fetch(`https://api.postalpincode.in/pincode/${pin}`);
                const data = await res.json();

                if (!data || data[0].Status !== "Success") {
                    output.innerHTML = `<div class="text-danger">Delivery not available for this location.</div>`;
                    return;
                }

                const office = data[0].PostOffice[0];
                const days = estimateDays(office.State);

                output.innerHTML = `
                    <div class="alert alert-success">
                        ✔ Delivery available to <b>${office.District}, ${office.State}</b><br>
                        🚚 Estimated Delivery: <b>${days} days</b>
                    </div>
                `;
            } catch {
                output.innerHTML = `<div class="text-danger">Error checking delivery.</div>`;
            }
        });
    })();


    // ======================================================
    // 5. FADE-IN ON LOAD FOR CARDS
    // ======================================================
    (() => {
        document.querySelectorAll(".product-card, .category-card")
            .forEach(card => card.classList.add("fade-in"));
    })();


    // ======================================================
    // 6. PRODUCT CARD SLIDESHOW (Category/List Pages)
    // ======================================================
    (() => {
        const cardContainers = document.querySelectorAll(".product-img-container");
        if (!cardContainers.length) return;

        cardContainers.forEach(container => {

            let images, img, prev, next;

            try {
                images = JSON.parse(container.dataset.images);
            } catch {
                return; // skip container with invalid data
            }

            img = container.querySelector(".product-img-slide");
            prev = container.querySelector(".prod-prev");
            next = container.querySelector(".prod-next");

            if (!img || !images.length) return;

            let index = 0;
            let interval = null;

            const updateImage = () => smoothUpdateImage(img, images[index]);

            const startAuto = () => {
                stopAuto();
                interval = setInterval(() => {
                    index = (index + 1) % images.length;
                    updateImage();
                }, 1200 + Math.random() * 1500);
            };

            const stopAuto = () => interval && clearInterval(interval);

            container.addEventListener("mouseenter", startAuto);
            container.addEventListener("mouseleave", () => {
                stopAuto();
                index = 0;
                updateImage();
            });

            prev?.addEventListener("click", e => {
                e.preventDefault();
                stopAuto();
                index = (index - 1 + images.length) % images.length;
                updateImage();
            });

            next?.addEventListener("click", e => {
                e.preventDefault();
                stopAuto();
                index = (index + 1) % images.length;
                updateImage();
            });
        });
    })();


    // ======================================================
    // 7. PRODUCT DETAIL — MAIN IMAGE SLIDER
    // ======================================================
    (() => {
        const containers = document.querySelectorAll(".pd-main-img-container");
        if (!containers.length) return;

        containers.forEach(container => {

            let images;
            try {
                images = JSON.parse(container.dataset.images);
            } catch {
                return;
            }

            const img = container.querySelector(".pd-main-img");
            const prev = container.querySelector(".pd-prev");
            const next = container.querySelector(".pd-next");
            const thumbs = container.parentElement.querySelectorAll(".pd-thumb");

            if (!img || !images.length) return;

            let index = 0;
            let interval;

            const update = () => {
                smoothUpdateImage(img, images[index]);
                thumbs.forEach(t => t.classList.remove("active"));
                thumbs[index]?.classList.add("active");
            };

            const startAuto = () => {
                stopAuto();
                interval = setInterval(() => {
                    index = (index + 1) % images.length;
                    update();
                }, 2200);
            };

            const stopAuto = () => interval && clearInterval(interval);

            next?.addEventListener("click", e => {
                e.preventDefault();
                stopAuto();
                index = (index + 1) % images.length;
                update();
            });

            prev?.addEventListener("click", e => {
                e.preventDefault();
                stopAuto();
                index = (index - 1 + images.length) % images.length;
                update();
            });

            thumbs.forEach((t, i) => {
                t.addEventListener("click", () => {
                    index = i;
                    update();
                    stopAuto();
                });
            });

            container.addEventListener("mouseenter", stopAuto);
            container.addEventListener("mouseleave", startAuto);

            update();
            startAuto();
        });
    })();


    // ======================================================
    // 8. SIZE + COLOR SELECTORS
    // ======================================================
    (() => {
        // Size
        const sizeBtns = document.querySelectorAll(".pd-size-option");
        const sizeInput = document.getElementById("selectedSize");

        sizeBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                sizeBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                if (sizeInput) sizeInput.value = btn.dataset.size;
            });
        });

        // Color
        const colorBtns = document.querySelectorAll(".pd-color-option");
        const colorInput = document.getElementById("selectedColor");

        colorBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                colorBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                if (colorInput) colorInput.value = btn.dataset.color;
            });
        });
    })();

});

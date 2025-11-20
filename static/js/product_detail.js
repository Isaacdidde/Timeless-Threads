document.addEventListener("DOMContentLoaded", () => {

  // ======================================================
  // PRODUCT GALLERY (Main Image + Thumbnails + Auto-slide)
  //
  // Features:
  //   - Clicking thumbnails swaps the main image
  //   - Prev/Next buttons cycle gallery images
  //   - Auto-slide runs every 3.5s
  //   - Auto-slide pauses on hover and resumes on mouse leave
  // ======================================================

  const main = document.getElementById("mainImage");
  const thumbs = [...document.querySelectorAll(".thumb")];

  // Extract image sources from thumb list
  let images = thumbs.map(t => t.src);
  let idx = 0;

  // Smooth switch to selected image index
  function showImage(i) {
    idx = i;
    main.classList.add("fade");

    setTimeout(() => {
      main.src = images[idx];

      // Highlight the active thumbnail
      thumbs.forEach((t, j) => t.classList.toggle("active", j === idx));

      main.classList.remove("fade");
    }, 150);
  }

  // Thumbnail click → change image
  thumbs.forEach((thumb, i) => {
    thumb.addEventListener("click", () => showImage(i));
  });

  // Prev / Next buttons
  document.getElementById("btnPrev").addEventListener("click", () =>
    showImage((idx - 1 + images.length) % images.length)
  );

  document.getElementById("btnNext").addEventListener("click", () =>
    showImage((idx + 1) % images.length)
  );

  // Auto-slide every 3.5s
  let autoSlide = setInterval(() => showImage((idx + 1) % images.length), 3500);

  // Stop auto-slide when hovering over main gallery
  const galleryMain = document.getElementById("galleryMain");

  galleryMain.addEventListener("mouseenter", () => clearInterval(autoSlide));

  galleryMain.addEventListener("mouseleave", () => {
    autoSlide = setInterval(() => showImage((idx + 1) % images.length), 3500);
  });

  // ======================================================
  // SIZE & COLOR SELECTORS
  //
  // - Highlight selection on click
  // - Update hidden inputs (`selectedSize`, `selectedColor`)
  // Disable "Add to Cart" if required fields are missing
  // - Cosmetics skip size/color requirement
  // ======================================================

  const sizeEls = document.querySelectorAll(".size-pill");
  const colorEls = document.querySelectorAll(".color-dot");
  const selectedSize = document.getElementById("selectedSize");
  const selectedColor = document.getElementById("selectedColor");
  const addBtn = document.getElementById("addBtn");

  // Using template-rendered category to detect cosmetics
  const isCosmetics = "{{ product.category|lower }}" === "cosmetics";

  // Enable/Disable Add-to-Cart button based on selection rules
  function validateAddBtn() {
    if (isCosmetics) {
      addBtn.disabled = false; // Cosmetics need no size/color
      return;
    }

    const sizeOK = sizeEls.length === 0 || selectedSize.value;
    const colorOK = colorEls.length === 0 || selectedColor.value;

    addBtn.disabled = !(sizeOK && colorOK);
  }

  // Size selection behavior
  sizeEls.forEach(el => {
    el.addEventListener("click", () => {
      sizeEls.forEach(s => s.classList.remove("active"));
      el.classList.add("active");
      selectedSize.value = el.dataset.size;
      validateAddBtn();
    });
  });

  // Color selection behavior
  colorEls.forEach(el => {
    el.addEventListener("click", () => {
      colorEls.forEach(c => c.classList.remove("active"));
      el.classList.add("active");
      selectedColor.value = el.dataset.color;
      validateAddBtn();
    });
  });

  // Run initial validation in case defaults exist
  validateAddBtn();

  // ======================================================
  // STAR HELPERS
  //
  // Utility function used by both new-review and edit-review
  // displays. Highlights stars visually based on selected rating.
  // ======================================================
  function highlightStars(stars, count) {
    stars.forEach((s, i) => {
      s.classList.toggle("active", i < count);
    });
  }

  // ======================================================
  // NEW REVIEW STAR SELECTOR
  //
  // Clicking a star sets:
  //   - hidden input value #newRating
  //   - visual highlight of selected stars
  // ======================================================
  const newStars = document.querySelectorAll(".new-star");
  const newRating = document.getElementById("newRating");

  newStars.forEach((star, i) => {
    star.addEventListener("click", () => {
      const rating = i + 1;
      newRating.value = rating;
      highlightStars(newStars, rating);
    });
  });

  // ======================================================
  // EDIT REVIEW LOGIC
  //
  // Features:
  //   - Show/Hide edit form on button click
  //   - Update rating stars inside edit form
  // ======================================================

  // Show edit box for selected review
  document.querySelectorAll(".edit-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.getElementById("edit-" + btn.dataset.id).style.display = "block";
    });
  });

  // Hide edit box when clicking Cancel
  document.querySelectorAll(".cancel-edit").forEach(btn => {
    btn.addEventListener("click", () => {
      document.getElementById("edit-" + btn.dataset.id).style.display = "none";
    });
  });

  // Edit-form star rating
  document.querySelectorAll(".edit-star").forEach(star => {
    star.addEventListener("click", () => {
      const wrapper = star.closest(".review-edit");
      const ratingInput = wrapper.querySelector(".edit-rating");
      const stars = wrapper.querySelectorAll(".edit-star");
      const rating = parseInt(star.dataset.value);

      ratingInput.value = rating;
      highlightStars(stars, rating);
    });
  });

  // ======================================================
  // RATING BAR FILLERS
  //
  // Used for displaying:
  //   - percentage bars
  //   - review rating distributions
  // ======================================================
  document.querySelectorAll(".bar-fill").forEach(el => {
    el.style.width = el.dataset.pct + "%";
  });

}); // END DOMContentLoaded

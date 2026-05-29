// FILENAME: js/main.js

// ── Auto-correct toggle ───────────────────────────────────────────────────── //

const toggleEl = document.getElementById("autocorrect-toggle");
if (toggleEl) {
    toggleEl.checked = localStorage.getItem("autocorrect") === "true";

    toggleEl.addEventListener("change", () => {
        localStorage.setItem("autocorrect", toggleEl.checked);
        if (toggleEl.checked) {
            window.closePopup?.();
        }
    });
}
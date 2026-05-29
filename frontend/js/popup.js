// FILENAME: js/popup.js

const popupEl       = document.getElementById("popup");
const suggestionsEl = document.getElementById("suggestions-list");
const closeBtn      = document.getElementById("popup-close");
const hintEl        = document.querySelector(".popup-hint");

let _suggestions = [];

const BADGE_CLASSES = ["badge-blue", "badge-green", "badge-orange"];
const WORD_CLASSES  = ["word-blue",  "word-green",  "word-orange"];

// ── Show / hide ───────────────────────────────────────────────────────────── //

function showPopup(suggestions, wordRange) {
    _suggestions = suggestions.slice(0, 3);
    if (_suggestions.length === 0) return;

    const autoCorrect = document.getElementById("autocorrect-toggle")?.checked;
    if (autoCorrect) {
        window.replaceWord?.(_suggestions[0]);
        return;
    }

    renderSuggestions();
    positionPopup(wordRange);
    popupEl.classList.add("visible");
}

function closePopup() {
    popupEl.classList.remove("visible");
    _suggestions = [];
}

window.showPopup  = showPopup;
window.closePopup = closePopup;


function renderSuggestions() {
    suggestionsEl.innerHTML = "";

    _suggestions.forEach((word, i) => {
        const item = document.createElement("div");
        item.className = "suggestion-item";

        const badge = document.createElement("span");
        badge.className = `suggestion-badge ${BADGE_CLASSES[i]}`;
        badge.textContent = i + 1;

        const label = document.createElement("span");
        label.className = `suggestion-word ${WORD_CLASSES[i]}`;
        label.textContent = word;

        const action = document.createElement("span");
        action.className = "suggestion-action";
        action.textContent = "Replace";

        item.appendChild(badge);
        item.appendChild(label);
        item.appendChild(action);
        item.addEventListener("click", () => acceptSuggestion(i));
        suggestionsEl.appendChild(item);
    });

    if (hintEl) {
        const keys = ["1", "2", "3"].slice(0, _suggestions.length).join(", ");
        hintEl.textContent = `Press ${keys} to choose`;
    }
}

function positionPopup(wordRange) {
    const rect     = wordRange.getBoundingClientRect();
    const wrapRect = document.getElementById("editor-wrap").getBoundingClientRect();

    let top  = rect.bottom - wrapRect.top + 8;
    let left = rect.left   - wrapRect.left;

    const maxLeft = wrapRect.width - 348;
    left = Math.max(0, Math.min(left, maxLeft));

    if (top + 160 > wrapRect.height) {
        top = rect.top - wrapRect.top - 160;
    }

    popupEl.style.top  = `${top}px`;
    popupEl.style.left = `${left}px`;
}

function acceptSuggestion(index) {
    const word = _suggestions[index];
    if (!word) return;
    window.replaceWord?.(word);
    closePopup();
}


closeBtn?.addEventListener("click", closePopup);

document.addEventListener("keydown", (e) => {
    if (!popupEl.classList.contains("visible")) return;
    const n = parseInt(e.key, 10);
    if (n >= 1 && n <= 3 && _suggestions[n - 1]) {
        e.preventDefault();
        acceptSuggestion(n - 1);
        return;
    }
    if (e.key === "Escape") closePopup();
});

// Close on outside click
document.addEventListener("mousedown", (e) => {
    if (!popupEl.classList.contains("visible")) return;
    if (!popupEl.contains(e.target)) closePopup();
});
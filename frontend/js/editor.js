// FILENAME: js/editor.js

const TYPING_DEBOUNCE_MS = 500;

const editorEl = document.getElementById("editor-display");
const wcEl     = document.getElementById("word-count");
const dotEl    = document.getElementById("status-dot");
const statusEl = document.getElementById("status-text");

let debounceTimer = null;

// ── Word count ────────────────────────────────────────────────────────────── //

function updateWordCount() {
    const text = editorEl.innerText || "";
    const n = text.trim().split(/\s+/).filter(Boolean).length;
    wcEl.textContent = `Words: ${n}`;
}

// ── Status dot ────────────────────────────────────────────────────────────── //

function setStatus(state) {
    // "ok" → green dot, "error" → red dot (has-issues class matches your CSS)
    dotEl.className = state === "error" ? "dot has-issues" : "dot";
    const labels = { ok: "No issues", error: "Misspelling detected", checking: "Checking…" };
    statusEl.textContent = labels[state] ?? "No issues";
}

// ── Get word under caret ──────────────────────────────────────────────────── //

function getCaretWord() {
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) return null;

    const range = sel.getRangeAt(0);
    if (!range.collapsed) return null;

    const node = range.startContainer;
    if (node.nodeType !== Node.TEXT_NODE) return null;

    const text   = node.textContent;
    const offset = range.startOffset;

    let start = offset;
    while (start > 0 && /[^\s.,!?;:]/.test(text[start - 1])) start--;

    let end = offset;
    while (end < text.length && /[^\s.,!?;:]/.test(text[end])) end++;

    const word = text.slice(start, end).replace(/[^a-zA-ZÀ-ÿ\u0100-\u017F'-]/g, "");
    if (word.length < 2) return null;

    const wordRange = document.createRange();
    wordRange.setStart(node, start);
    wordRange.setEnd(node, end);

    return { word, range: wordRange };
}

function getLastWord() {
    const sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) return null;

    const range = sel.getRangeAt(0);
    if (!range.collapsed) return null;

    const node = range.startContainer;
    if (node.nodeType !== Node.TEXT_NODE) return null;

    const text   = node.textContent;
    const offset = range.startOffset;

    let end = offset - 1;
    while (end >= 0 && /[\s.,!?;:]/.test(text[end])) end--;
    if (end < 0) return null;

    let start = end;
    while (start > 0 && /[^\s.,!?;:]/.test(text[start - 1])) start--;

    const word = text.slice(start, end + 1).replace(/[^a-zA-ZÀ-ÿ\u0100-\u017F'-]/g, "");
    if (word.length < 2) return null;

    const wordRange = document.createRange();
    wordRange.setStart(node, start);
    wordRange.setEnd(node, end + 1);

    return { word, range: wordRange };
}

// ── Replace word in editor ────────────────────────────────────────────────── //

function replaceWord(replacement) {
    if (!window._lastCheckedRange) return;

    const range = window._lastCheckedRange;
    range.deleteContents();
    range.insertNode(document.createTextNode(replacement));

    const sel = window.getSelection();
    range.collapse(false);
    sel.removeAllRanges();
    sel.addRange(range);

    window._lastCheckedRange = null;
    setStatus("ok");
    updateWordCount();
}

// ── Core spell-check function ─────────────────────────────────────────────── //

async function spellCheck(hit) {
    if (!hit) return;

    setStatus("checking");
    console.log("[spellcheck] checking:", hit.word);

    const result = await getSpellingSuggestions(hit.word);
    console.log("[spellcheck] result:", result);

    // api.js now returns { word, correct, suggestions[] }
    if (!result || !Array.isArray(result.suggestions)) {
        setStatus("ok");
        return;
    }

    if (result.correct || result.suggestions.length === 0) {
        setStatus("ok");
        window.closePopup?.();
        return;
    }

    setStatus("error");
    window._lastCheckedRange = hit.range.cloneRange();
    window._lastCheckedWord  = hit.word;
    window.showPopup?.(result.suggestions, hit.range);
}


editorEl.addEventListener("input", () => {
    updateWordCount();
    clearTimeout(debounceTimer);

    const text = editorEl.innerText || "";
    const lastChar = text[text.length - 1] || "";
    const justFinishedWord = /[\s.,!?;:]/.test(lastChar);

    debounceTimer = setTimeout(async () => {
        const hit = justFinishedWord ? getLastWord() : getCaretWord();
        await spellCheck(hit);
    }, TYPING_DEBOUNCE_MS);
});


editorEl.addEventListener("click", async () => {
    clearTimeout(debounceTimer);
    const hit = getCaretWord();
    await spellCheck(hit);
});

// Init
updateWordCount();
setStatus("ok");
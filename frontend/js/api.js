// FILENAME: js/api.js
const API_BASE_URL = "http://127.0.0.1:8000";

async function getSpellingSuggestions(word) {
    if (!word || word.trim() === "") {
        return { word, correct: true, suggestions: [] };
    }
    try {
        const encoded = encodeURIComponent(word.trim());
        const response = await fetch(`${API_BASE_URL}/api/check?word=${encoded}`);
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        return await response.json(); // { word, correct, suggestions }
    } catch (error) {
        console.error("Spell-check fetch failed:", error);
        return { word, correct: true, suggestions: [] };
    }
}
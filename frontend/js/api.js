// FILENAME: api.js
const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * sends a word to the FastAPI backend spellchecker via HTTP GET.
 * @param {string} word - the word to check
 * @returns {Promise<string[]>} [original, best_suggestion, second_suggestion]
 */
async function getSpellingSuggestions(word) {
    // if no word was entered
    if ( !word || word.trim() === "" ) {
        return [word, "", ""]
    }

    try {
        const encodedWord = encodeURIComponent(word.trim());
        const response = await fetch(`${API_BASE_URL}/api/check?word=${encodedWord}`);
        if ( !response.ok ) throw new Error(`Server status error: ${response.status}`);
        const data = await response.json();
        return data.suggestions;

    } catch ( error ) {
        console.error("Failed to fetch spelling suggestions:", error);
        return [word, "", ""];
    }
}
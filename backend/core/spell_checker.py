# FILENAME: core/spell_checker.py

from core.bk_tree import BKTree
from core.sorter import sort_candidates

QUERY_THRESHOLD = 2.5
MAX_SUGGESTIONS = 3


class SpellChecker:
    def __init__(self):
        self._tree = BKTree()
        self._wordset: set[str] = set()

    def load_wordlist(self, words: list[str]) -> None:
        for word in words:
            w = word.strip().lower()
            if w and w not in self._wordset:
                self._wordset.add(w)
                self._tree.insert(w)

    @property
    def wordlist_size(self) -> int:
        return len(self._wordset)

    def is_correct(self, word: str) -> bool:
        return word.lower() in self._wordset

    def check(self, word: str, max_suggestions: int = MAX_SUGGESTIONS) -> list[str]:
        normalised = word.lower().strip()
        if not normalised:
            return []

        # Exact match — correct, no suggestions needed
        if self.is_correct(normalised):
            return []

        # BK-Tree approximate search
        candidates = self._tree.query(normalised, QUERY_THRESHOLD)

        if not candidates:
            candidates = self._tree.query(normalised, QUERY_THRESHOLD + 1.5)

        if not candidates:
            return []   

        ranked = sort_candidates(candidates, normalised)
        return [w for w, _ in ranked[:max_suggestions]]
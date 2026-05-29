# FILENAME: core/sorter.py


#  

from core.keyboard_proximity import substitution_cost


# characters that match at the same position
def _positional_similarity(word: str, candidate: str) -> int:
    return sum(1 for a, b in zip(word, candidate) if a == b)

# computing for proximity score
def _keyboard_proximity_score(input_word: str, candidate: str) -> float:
    return sum(
        substitution_cost(a, b)
        for a, b in zip(input_word, candidate)
        if a != b
    )

def _sort_key(candidate: tuple, input_word: str) -> tuple:
    word, distance = candidate
    length_penalty = abs(len(word) - len(input_word)) * 0.1
    pos_sim = -_positional_similarity(input_word, word)
    kb_score = _keyboard_proximity_score(input_word, word)
    return (distance, length_penalty, pos_sim, kb_score, word)

def sort_candidates(candidates: list[tuple], input_word: str) -> list[tuple]:
    return sorted(candidates, key=lambda c: _sort_key(c, input_word))
# FILENAME: bk_tree.py

from core.levenshtein import WeightedLevenshtein

class BKNode:
    # node for BK tree
    def __init__(self, word: str):
        self.word = word
        self.children = {}

class BKTree:
    # BK Tree data structure
    def __init__(self):
        self.root = None

    def _distance(self, target, source) -> float:
        # imports WeightedLevenshtein to solve for distance
        lev = WeightedLevenshtein(target, source)
        return lev.minDistance(target, source)

    def insert(self, word: str):
        if self.root is None:
            self.root = BKNode(word)
            return
        
        current = self.root
        while True:
            distance = self._distance(current.word, word)
            if distance not in current.children:
                current.children[distance] = BKNode(word)
                break
            else:
                current= current.children[distance]

    def query(self, word: str, threshold: float) -> list:
        if self.root is None:
            return []
        
        results = []
        stack = [self.root]

        while stack:
            current = stack.pop(0)
            distance = self._distance(current.word, word)

            if distance <= threshold:
                results.append((current.word, distance))

            for edge, child in current.children.items():
                if (distance - threshold) <= edge <= (distance + threshold):
                    stack.append(child)

        return results
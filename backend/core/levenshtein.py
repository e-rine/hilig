# FILENAME: levenshtein.py

class Levenshtein:
    def __init__(self, source, target):
        # cache matrix grid
        self.cache = [ [float("inf")]  * (len(target) + 1) for i in range(len(source) + 1)]
        self.source_len = len(source)
        self.target_len = len(target)

        # initialize base cases for cache
        for i in range(self.source_len + 1):
            self.cache[i][0] = i

        for j in range(self.target_len + 1):
            self.cache[0][j] = j

    def copy(self, k, l) -> int:
        # diagonal neighbor (up-left)
        # match or substitute
        return self.cache[k - 1][l - 1]

    def insert(self, k, l) -> int:
        # left neighbor --- insert a character
        return 1 + self.cache[k][l - 1]

    def delete(self, k, l) -> int:
        # upper neighbor --- delete a character
        return 1 + self.cache[k - 1][l]
    
    def sub_cost(self, x, y) -> int:
        # substitution cost
        return 0 if x == y else 1

    # +--- MAIN METHOD ---+ #
    def minDistance(self, source, target) -> float:
        for k in range(1, self.source_len + 1):
            for l in range(1, self.target_len + 1):
                if (source[k - 1] == target[l - 1]):
                    self.cache[k][l] = self.copy(k, l)

                else:
                    self.cache[k][l] = min(
                        self.copy(k, l) + self.sub_cost(source[k - 1], target[l - 1]),
                        self.insert(k, l),
                        self.delete(k, l)
                    )
        
        return self.cache[self.source_len][self.target_len]
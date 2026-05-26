# FILENAME: levenshtein.py

from types import SimpleNamespace

class Levenshtein:
    def __init__(self, source, target):
        # direction constants
        self.DIRECTIONS = SimpleNamespace(
            UP      = (-1, 0),
            LEFT    = (0, -1),
            UP_LEFT = (-1, -1)
        )
        
        # cache matrix grid
        self.cache = [ [float("inf")]  * (len(target) + 1) for i in range(len(source) + 1)]
        self.source_len = len(source)
        self.target_len = len(target)

        # initialize base cases for cache
        for i in range(self.source_len + 1):
            self.cache[i][0] = i

        for j in range(self.target_len + 1):
            self.cache[0][j] = j

    # +--- MAIN METHODS ---+ #
    def copy(self):
        pass

    def insert(self):
        pass

    def delete(self):
        pass

    def minDistance(self, source, target):
        for k in range(self.source_len + 1):
            for l in range(self.target_len + 1):
                # solve for current neighbor positions
                delta_row, delta_col = self.DIRECTIONS.UP
                up_nbor = self.cache[delta_row + k][delta_col + l]
                
                delta_row, delta_col = self.DIRECTIONS.LEFT
                left_nbor = self.cache[delta_row + k][delta_col + l]
                
                delta_row, delta_col = self.DIRECTIONS.UP_LEFT
                upleft_nbor = self.cache[delta_row + k][delta_col + l]

                if (source[k - 1] == target[l - 1]):
                    #copy
                    self.cache[k][l] = upleft_nbor
                    pass

                else:
                    self.cache[k][l] = 1 + min(up_nbor, left_nbor, upleft_nbor)
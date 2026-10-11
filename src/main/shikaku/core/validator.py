from typing import List
from .types import Rect, Puzzle


class Validator:
    """Проверяет корректность прямоугольников и решения."""

    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle

    def is_rect_valid(self, rect: Rect) -> bool:
        if (rect.row < 0 or rect.col < 0
                or rect.row + rect.height > self.puzzle.size
                or rect.col + rect.width > self.puzzle.size):
            return False
        count = 0
        value = None
        for r, c in rect.cells():
            v = self.puzzle.grid[r][c]
            if v is not None:
                count += 1
                value = v
        return count == 1 and value == rect.area

    def is_solved(self, rects: List[Rect]) -> bool:
        if not rects:
            return False
        if not all(self.is_rect_valid(r) for r in rects):
            return False
        covered = [[False] * self.puzzle.size for _ in range(self.puzzle.size)]
        for rect in rects:
            for r, c in rect.cells():
                if covered[r][c]:
                    return False
                covered[r][c] = True
        return all(all(row) for row in covered)
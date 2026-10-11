import os
import sys
import unittest

# добавляем src/main в sys.path, чтобы работал import shikaku
HERE = os.path.dirname(os.path.abspath(__file__))
SRC_MAIN = os.path.abspath(os.path.join(HERE, "..", "..", "main"))
if SRC_MAIN not in sys.path:
    sys.path.insert(0, SRC_MAIN)

from shikaku.core.types import Puzzle, Rect
from shikaku.core.validator import Validator


class TestValidator(unittest.TestCase):

    def _puzzle(self):
        grid = [[None, None, 6],
                [None, None, None],
                [2, None, None]]
        return Puzzle(size=3, grid=grid, solution=[])

    def test_valid_rect(self):
        v = Validator(self._puzzle())
        self.assertTrue(v.is_rect_valid(Rect(0, 0, 2, 3)))

    def test_invalid_area(self):
        v = Validator(self._puzzle())
        self.assertFalse(v.is_rect_valid(Rect(0, 2, 1, 1)))

    def test_solved(self):
        v = Validator(self._puzzle())
        rects = [Rect(0, 0, 2, 3), Rect(2, 0, 1, 2), Rect(2, 2, 1, 1)]
        self.assertTrue(v.is_solved(rects))

    def test_overlap_not_solved(self):
        v = Validator(self._puzzle())
        rects = [Rect(0, 0, 2, 3), Rect(0, 0, 1, 1)]
        self.assertFalse(v.is_solved(rects))


if __name__ == "__main__":
    unittest.main()
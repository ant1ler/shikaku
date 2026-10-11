import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_MAIN = os.path.abspath(os.path.join(HERE, "..", "..", "main"))
if SRC_MAIN not in sys.path:
    sys.path.insert(0, SRC_MAIN)

from shikaku.core.generator import PuzzleGenerator
from shikaku.core.validator import Validator


class TestGenerator(unittest.TestCase):

    def test_generated_puzzle_is_solvable(self):
        gen = PuzzleGenerator(seed=42)
        for size in (3, 6, 9):
            puzzle = gen.generate(size)
            v = Validator(puzzle)
            self.assertTrue(v.is_solved(puzzle.solution),
                            f"Пазл {size}x{size} не решается эталонным решением")

    def test_unique_generator(self):
        gen = PuzzleGenerator()
        a = gen.generate_unique(6)
        b = gen.generate_unique(6)
        self.assertNotEqual(
            PuzzleGenerator._fingerprint(a),
            PuzzleGenerator._fingerprint(b),
        )
        
    


if __name__ == "__main__":
    unittest.main()
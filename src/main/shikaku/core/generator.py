import hashlib
import random
import time
from collections import deque
from typing import List, Deque
from .types import Puzzle, Rect


class PuzzleGenerator:
    """Генерирует уникальные решаемые пазлы без подсказок '1'.

    Гарантии:
      • нет регионов площадью 1 (нет подсказок «1»);
      • нет регионов, занимающих всё поле целиком;
      • нет регионов больше MAX_REGION_FRACTION от площади поля.
    """

    RECENT_LIMIT = 200
    MIN_REGION = 2
    MAX_REGION_FRACTION = 0.35
    MAX_REGION_ABS = 25

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)
        self._recent: Deque[str] = deque(maxlen=self.RECENT_LIMIT)

    def generate(self, size: int) -> Puzzle:
        if size < 2:
            raise ValueError("Размер поля должен быть >= 2")
        return self._generate_with_seed(size, self.rng.randrange(2**32))

    def generate_unique(self, size: int, max_attempts: int = 80) -> Puzzle:
        if size < 2:
            raise ValueError("Размер поля должен быть >= 2")
        puzzle = None
        for _ in range(max_attempts):
            seed = time.time_ns() ^ random.getrandbits(32)
            puzzle = self._generate_with_seed(size, seed)
            fp = self._fingerprint(puzzle)
            if fp not in self._recent:
                self._recent.append(fp)
                return puzzle
        return puzzle

    def generate_with_seed(self, size: int, seed: int) -> Puzzle:
        """Фиксированный пазл по seed — для ежедневного вызова."""
        if size < 2:
            raise ValueError("Размер поля должен быть >= 2")
        return self._generate_with_seed(size, seed)

    # ------------------------------------------------------------------
    def _max_region(self, size: int) -> int:
        fraction = max(self.MIN_REGION, int(size * size * self.MAX_REGION_FRACTION))
        return min(fraction, self.MAX_REGION_ABS)

    def _generate_with_seed(self, size: int, seed: int) -> Puzzle:
        rng = random.Random(seed)
        grid = [[None] * size for _ in range(size)]
        solution: List[Rect] = []
        max_area = self._max_region(size)
        self._fill_region(0, 0, size, size, grid, solution, rng, max_area)
        return Puzzle(size=size, grid=grid, solution=solution)

    def _fill_region(self, r, c, h, w, grid, solution, rng, max_area):
        area = h * w
        can_keep = area >= self.MIN_REGION and area <= max_area

        if area < self.MIN_REGION:
            return

        if can_keep and (area <= 4 or rng.random() < 0.35):
            solution.append(Rect(r, c, h, w))
            rr = r + rng.randrange(h)
            cc = c + rng.randrange(w)
            grid[rr][cc] = area
            return

        cuts = []
        for cut in range(1, h):
            top = cut * w
            bot = (h - cut) * w
            if self.MIN_REGION <= top <= max_area and self.MIN_REGION <= bot <= max_area:
                cuts.append(("h", cut))
        for cut in range(1, w):
            left = cut * h
            right = (w - cut) * h
            if self.MIN_REGION <= left <= max_area and self.MIN_REGION <= right <= max_area:
                cuts.append(("v", cut))

        if not cuts:
            if area <= max_area:
                solution.append(Rect(r, c, h, w))
                rr = r + rng.randrange(h)
                cc = c + rng.randrange(w)
                grid[rr][cc] = area
            else:
                if h >= w and h > 1:
                    cut = h // 2
                    self._fill_region(r, c, cut, w, grid, solution, rng, max_area)
                    self._fill_region(r + cut, c, h - cut, w, grid, solution, rng, max_area)
                elif w > 1:
                    cut = w // 2
                    self._fill_region(r, c, h, cut, grid, solution, rng, max_area)
                    self._fill_region(r, c + cut, h, w - cut, grid, solution, rng, max_area)
            return

        direction, cut = rng.choice(cuts)
        if direction == "h":
            self._fill_region(r, c, cut, w, grid, solution, rng, max_area)
            self._fill_region(r + cut, c, h - cut, w, grid, solution, rng, max_area)
        else:
            self._fill_region(r, c, h, cut, grid, solution, rng, max_area)
            self._fill_region(r, c + cut, h, w - cut, grid, solution, rng, max_area)

    @staticmethod
    def _fingerprint(puzzle: Puzzle) -> str:
        parts = [f"{r},{c}={v}" for r, c, v in puzzle.clues()]
        raw = "|".join(parts).encode("utf-8")
        return hashlib.sha1(raw).hexdigest()
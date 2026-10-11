from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class Rect:
    """Прямоугольник на поле. row/col — верхний левый угол."""
    row: int
    col: int
    height: int
    width: int

    @property
    def area(self) -> int:
        return self.height * self.width

    def cells(self):
        for r in range(self.row, self.row + self.height):
            for c in range(self.col, self.col + self.width):
                yield r, c

    def overlaps(self, other: "Rect") -> bool:
        return not (
            self.row + self.height <= other.row
            or other.row + other.height <= self.row
            or self.col + self.width <= other.col
            or other.col + other.width <= self.col
        )

    def to_dict(self):
        return {
            "row": self.row, "col": self.col,
            "height": self.height, "width": self.width,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(d["row"], d["col"], d["height"], d["width"])


@dataclass
class Puzzle:
    """Сгенерированный пазл: подсказки + эталонное решение."""
    size: int
    grid: List[List[Optional[int]]]
    solution: List[Rect]

    def clues(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] is not None:
                    yield r, c, self.grid[r][c]

    def to_dict(self):
        return {
            "size": self.size,
            "grid": self.grid,
            "solution": [r.to_dict() for r in self.solution],
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            size=d["size"],
            grid=d["grid"],
            solution=[Rect.from_dict(r) for r in d["solution"]],
        )
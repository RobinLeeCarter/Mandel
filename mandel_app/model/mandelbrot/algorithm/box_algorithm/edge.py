from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from mandel_app import tuples


@dataclass
class Edge:
    x_min: int
    y_min: int

    def __post_init__(self):
        self.single_value: Optional[int] = None

    @property
    def bottom_left(self) -> tuples.PixelPoint:
        return tuples.PixelPoint(x=self.x_min, y=self.y_min)

    @property
    def top_right(self) -> tuples.PixelPoint:
        return tuples.PixelPoint(x=self.x_min, y=self.y_min)

    def same_value(self, single_value: int):
        # noinspection PyAttributeOutsideInit
        self.single_value = single_value


@dataclass
class VerticalEdge(Edge):
    y_max: int

    @property
    def top_right(self) -> tuples.PixelPoint:
        return tuples.PixelPoint(x=self.x_min, y=self.y_max)


@dataclass
class HorizontalEdge(Edge):
    x_max: int

    @property
    def top_right(self) -> tuples.PixelPoint:
        return tuples.PixelPoint(x=self.x_max, y=self.y_min)

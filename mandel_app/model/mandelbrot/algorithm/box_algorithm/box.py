from __future__ import annotations
from dataclasses import dataclass
from typing import List, Callable

from mandel_app import tuples
from mandel_app.model.mandelbrot.server import server

from mandel_app.model.mandelbrot.algorithm.box_algorithm import edge


@dataclass
class Box:
    x_min: int
    y_min: int
    x_max: int  # inclusive
    y_max: int  # inclusive
    depth: int
    server: server.Server

    def __post_init__(self):
        self._left_edge = edge.VerticalEdge(
            x_min=self.x_min,
            y_min=self.y_min,
            y_max=self.y_max
        )
        self._right_edge = edge.VerticalEdge(
            x_min=self.x_max,
            y_min=self.y_min,
            y_max=self.y_max
        )
        self._bottom_edge = edge.HorizontalEdge(
            x_min=self.x_min,
            y_min=self.y_min,
            x_max=self.x_max
        )
        self._top_edge = edge.HorizontalEdge(
            x_min=self.x_min,
            y_min=self.y_max,
            x_max=self.x_max
        )
        self._edges: List[edge.Edge] = [self._left_edge, self._right_edge, self._bottom_edge, self._top_edge]
        self.filled = False
        self._children: List[Box] = []

    @property
    def _inside_bottom_left(self) -> tuples.PixelPoint:
        return tuples.PixelPoint(x=self.x_min+1, y=self.y_min+1)

    @property
    def _inside_top_right(self) -> tuples.PixelPoint:
        return tuples.PixelPoint(x=self.x_max-1, y=self.y_max-1)

    @property
    def x_size(self) -> int:
        return self.x_max - self.x_min + 1

    @property
    def y_size(self) -> int:
        return self.y_max - self.y_min + 1

    def call_method_at_depth(self, func: Callable[[Box], None], depth: int):
        if self.depth == depth:
            func(self)
        else:
            for child in self._children:
                child.call_method_at_depth(func, depth)

    def request_edge_compute(self):
        for edge_ in self._edges:
            if edge_.single_value is None:
                self.server.box_request(edge_.bottom_left, edge_.top_right, same_value=edge_.same_value)

    def request_inside_compute(self):
        if not self.filled:
            self.server.box_request(self._inside_bottom_left, self._inside_top_right, completed=self._set_filled)

    def _set_filled(self):
        # noinspection PyAttributeOutsideInit
        self.filled = True

    def check_if_can_fill(self):
        left_value = self._left_edge.single_value
        right_value = self._right_edge.single_value
        bottom_value = self._bottom_edge.single_value
        top_value = self._top_edge.single_value
        # print(f"left_value = {left_value}")
        if left_value is not None and right_value is not None and bottom_value is not None and top_value is not None:
            if left_value == right_value and left_value == bottom_value and left_value == top_value:
                self._fill_inside_box(left_value)

    def _fill_inside_box(self, value: int):
        if self._inside_bottom_left.x <= self._inside_top_right.x \
                and self._inside_bottom_left.y <= self._inside_top_right.y:
            self.server.fill_box_request(self._inside_bottom_left, self._inside_top_right,
                                         value=value, completed=self._set_filled)

    def spawn_children(self):
        if not self.filled:
            if self.x_size <= 4 or self.y_size <= 4:
                print("box too small to spawn")
                pass  # refuse to spawn, or just calculate

            x_mid_point = int((self.x_min + self.x_max) / 2)
            y_mid_point = int((self.y_min + self.y_max) / 2)

            # bottom left box_algorithm
            bottom_left = Box(x_min=self.x_min, y_min=self.y_min,
                              x_max=x_mid_point, y_max=y_mid_point,
                              depth=self.depth+1, server=self.server)
            bottom_right = Box(x_min=x_mid_point, y_min=self.y_min,
                               x_max=self.x_max, y_max=y_mid_point,
                               depth=self.depth+1, server=self.server)
            top_left = Box(x_min=self.x_min, y_min=y_mid_point,
                           x_max=x_mid_point, y_max=self.y_max,
                           depth=self.depth+1, server=self.server)
            top_right = Box(x_min=x_mid_point, y_min=y_mid_point,
                            x_max=self.x_max, y_max=self.y_max,
                            depth=self.depth+1, server=self.server)
            self._children.extend([bottom_left, bottom_right, top_left, top_right])

            left_value = self._left_edge.single_value
            right_value = self._right_edge.single_value
            bottom_value = self._bottom_edge.single_value
            top_value = self._top_edge.single_value
            if left_value is not None:
                bottom_left._left_edge.single_value = left_value
                top_left._left_edge.single_value = left_value
            if right_value is not None:
                bottom_right._right_edge.single_value = right_value
                top_right._right_edge.single_value = right_value
            if bottom_value is not None:
                bottom_left._bottom_edge.single_value = bottom_value
                bottom_right._bottom_edge.single_value = bottom_value
            if top_value is not None:
                top_left._top_edge.single_value = top_value
                top_right._top_edge.single_value = top_value

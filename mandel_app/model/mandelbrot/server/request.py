from __future__ import annotations
from dataclasses import dataclass

from typing import Optional, Callable, Union

import numpy as np
import cupy as cp

from mandel_app import tuples


@dataclass
class Request:
    bottom_left: tuples.PixelPoint
    top_right: tuples.PixelPoint
    same_value: Optional[Callable[[int], None]] = None
    completed: Optional[Callable[[], None]] = None

    def respond(self, iteration: Union[np.ndarray, cp.ndarray]):
        if self.same_value is not None:
            self.same_value_respond(iteration)
        if self.completed is not None:
            self.completed()

    def same_value_respond(self, iteration: Union[np.ndarray, cp.ndarray]):
        bottom_left_value = iteration[self.bottom_left.y, self.bottom_left.x]
        iteration_slice = iteration[self.bottom_left.y: self.top_right.y+1, self.bottom_left.x: self.top_right.x+1]
        # noinspection PyTypeChecker
        same_as_bottom_left: cp.ndarray = (iteration_slice == bottom_left_value)
        if same_as_bottom_left.all():
            self.same_value(bottom_left_value)

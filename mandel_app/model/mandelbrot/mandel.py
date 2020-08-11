from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np

from mandel_app import tuples


@dataclass
class Mandel:
    # region Setup
    centre: tuples.ComplexPoint
    shape: tuples.ImageShape
    size: float = 0.0
    size_per_gap: float = 0.0
    theta_degrees: int = 0
    expected_iterations_per_pixel: float = 0.0
    has_border: bool = False

    def __post_init__(self):
        self.original_shape = self.shape
        self.pan: Optional[tuples.PixelPoint] = None
        self.offset: tuples.PixelPoint = tuples.PixelPoint(x=0, y=0)
        self.iteration: Optional[np.ndarray] = None
        self.max_iteration: int = 0
        # one less gap than shape
        # eg. 4 pixels from [0 to size] have 3 gaps [0, 1, 2, 3]
        if self.size_per_gap == 0.0:
            if self.shape.y <= self.shape.x:
                self.size_per_gap = self.size / float(self.shape.y-1)
            else:
                self.size_per_gap = self.size / float(self.shape.x-1)

        self.time_taken: float = 0.0
        self.iterations_performed: int = 0
        self.iterations_per_pixel: float = 0.0
        self.final_iteration: int = 0

        # keep track of the contents of iteration at all times
        self.iteration_shape: tuples.ImageShape = self.shape
        self.iteration_offset: tuples.PixelPoint = tuples.PixelPoint(x=0, y=0)

    @property
    def x_size(self) -> float:
        return self.size_per_gap * float(self.shape.x-1)

    @property
    def y_size(self) -> float:
        return self.size_per_gap * float(self.shape.y-1)

    @property
    def theta_radians(self) -> float:
        return math.radians(self.theta_degrees)

    @property
    def x_unit(self) -> tuples.ComplexPoint:
        return tuples.ComplexPoint(math.cos(self.theta_radians), math.sin(self.theta_radians))

    @property
    def y_unit(self) -> tuples.ComplexPoint:
        return tuples.ComplexPoint(-math.sin(self.theta_radians), math.cos(self.theta_radians))
    # endregion

    # region Methods
    def pan_centre(self):
        new_centre_pixel = tuples.PixelPoint(
            x=float(self.shape.x)/2.0 + self.pan.x,
            y=float(self.shape.y)/2.0 + self.pan.y
        )
        self.centre = self.get_complex_point(new_centre_pixel)

    def add_border(self, border_x: int, border_y: int):
        # print(self.shape)
        new_shape = tuples.ImageShape(self.shape.x + border_x*2,
                                      self.shape.y + border_y*2)
        # print(new_shape)
        new_offset = tuples.PixelPoint(self.offset.x - border_x,
                                       self.offset.y - border_y)
        self.shape = new_shape
        # noinspection PyAttributeOutsideInit
        self.offset = new_offset
        self.has_border = True

    def remove_border(self):
        self.shape = self.original_shape
        # noinspection PyAttributeOutsideInit
        self.offset = tuples.PixelPoint(x=0, y=0)
        self.has_border = False

    def get_complex_point(self, pixel_point: tuples.PixelPoint) -> tuples.ComplexPoint:
        x_scale = (float(pixel_point.x) / float(self.shape.x)) - 0.5
        y_scale = (float(pixel_point.y) / float(self.shape.y)) - 0.5
        x_dist = x_scale * self.x_size
        y_dist = y_scale * self.y_size
        real = self.centre.real + x_dist * self.x_unit.real + y_dist * self.y_unit.real
        imag = self.centre.imag + x_dist * self.x_unit.imag + y_dist * self.y_unit.imag
        return tuples.ComplexPoint(real, imag)

    @property
    def centre_complex(self) -> complex:
        return complex(real=self.centre.real, imag=self.centre.imag)
    # endregion

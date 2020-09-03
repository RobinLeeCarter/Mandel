from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np

from mandel_app import tuples


@dataclass
class Mandel:
    # region Setup
    centre: complex
    shape: tuples.ImageShape
    size: float = 0.0
    size_per_gap: float = 0.0
    theta_degrees: int = 0
    expected_iterations_per_pixel: float = 0.0
    has_border: bool = False

    def __post_init__(self):
        # self.original_shape: tuples.ImageShape = self.shape
        self.pan: Optional[tuples.PixelPoint] = None
        # self.offset: tuples.PixelPoint = tuples.PixelPoint(x=0, y=0)
        self.iteration: Optional[np.ndarray] = None
        self.max_iteration: int = 0

        self.time_taken: float = 0.0
        self.iterations_performed: int = 0
        self.iterations_per_pixel: float = 0.0
        self.final_iteration: int = 0

        # keep track of the contents of iteration at all times
        # self.iteration_shape: tuples.ImageShape = self.shape
        # self.iteration_offset: tuples.PixelPoint = tuples.PixelPoint(x=0, y=0)

        # one less gap than shape
        # eg. 4 pixels from [0 to size] have 3 gaps [0, 1, 2, 3]
        if self.size_per_gap == 0.0:
            if self.shape.y <= self.shape.x:
                self.size_per_gap = self.size / float(self.shape.y-1)
            else:
                self.size_per_gap = self.size / float(self.shape.x-1)

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
    def x_unit(self) -> complex:
        return complex(math.cos(self.theta_radians), math.sin(self.theta_radians))

    @property
    def y_unit(self) -> complex:
        return complex(-math.sin(self.theta_radians), math.cos(self.theta_radians))
    # endregion

    def lite_copy(self,
                  centre: Optional[complex] = None,
                  shape: Optional[tuples.ImageShape] = None,
                  size: Optional[float] = None,
                  size_per_gap: Optional[float] = None,
                  theta_degrees: Optional[int] = None,
                  expected_iterations_per_pixel: Optional[float] = None,
                  has_border: Optional[bool] = None
                  ) -> Mandel:
        centre = self._if_none(centre, self.centre)
        shape = self._if_none(shape, self.shape)
        size = self._if_none(size, self.size)
        size_per_gap = self._if_none(size_per_gap, self.size_per_gap)
        theta_degrees = self._if_none(theta_degrees, self.theta_degrees)
        expected_iterations_per_pixel = self._if_none(expected_iterations_per_pixel, self.expected_iterations_per_pixel)
        has_border = self._if_none(has_border, self.has_border)

        return Mandel(
            centre=centre,
            shape=shape,
            size=size,
            size_per_gap=size_per_gap,
            theta_degrees=theta_degrees,
            expected_iterations_per_pixel=expected_iterations_per_pixel,
            has_border=has_border
        )

    # region Methods
    @staticmethod
    def _if_none(var, val):
        if var is None:
            return val
        return var

    # def pan_centre(self, pan: tuples.PixelPoint):
    #     new_centre_pixel = tuples.PixelPoint(
    #         x=float(self.shape.x)/2.0 + pan.x,
    #         y=float(self.shape.y)/2.0 + pan.y
    #     )
    #     self.centre = self.get_complex_from_frame_point(new_centre_pixel)

    # def add_border(self, border_x: int, border_y: int):
    #     # print(self.shape)
    #     new_shape = tuples.ImageShape(self.shape.x + border_x*2,
    #                                   self.shape.y + border_y*2)
    #     # print(new_shape)
    #     new_offset = tuples.PixelPoint(self.offset.x - border_x,
    #                                    self.offset.y - border_y)
    #     self.shape = new_shape
    #     # noinspection PyAttributeOutsideInit
    #     self.offset = new_offset
    #     self.has_border = True

    # def remove_border(self):
    #     self.shape = self.original_shape
    #     # noinspection PyAttributeOutsideInit
    #     self.offset = tuples.PixelPoint(x=0, y=0)
    #     self.has_border = False

    # def old_get_complex_from_pixel(self, pixel_point: tuples.PixelPoint) -> complex:
    #     x_scale = (float(pixel_point.x) / float(self.shape.x)) - 0.5
    #     y_scale = (float(pixel_point.y) / float(self.shape.y)) - 0.5
    #     x_dist = x_scale * self.x_size
    #     y_dist = y_scale * self.y_size
    #
    #     return self.centre + x_dist * self.x_unit + y_dist * self.y_unit

    def get_complex_from_frame_point(self,
                                     frame_shape: tuples.ImageShape,
                                     frame_point: tuples.PixelPoint
                                     ) -> complex:
        # print(f"frame_shape: {frame_shape}")
        # print(f"frame_point: {frame_point}")
        # print(f"shape: {self.shape}")
        x_pixels_from_center = frame_point.x - 0.5*(frame_shape.x-1)
        y_pixels_from_center = frame_point.y - 0.5*(frame_shape.y-1)

        # x_scale = (float(self.offset.x + frame_point.x) / float(self.shape.x)) - 0.5
        # y_scale = (float(self.offset.y + frame_point.y) / float(self.shape.y)) - 0.5
        # x_scale = (float(frame_point.x) / float(self.shape.x)) - 0.5
        # y_scale = (float(frame_point.y) / float(self.shape.y)) - 0.5

        # x_scale = (x_pixels_from_center / float(self.shape.x))
        # y_scale = (y_pixels_from_center / float(self.shape.y))
        # x_dist = x_scale * self.x_size
        # y_dist = y_scale * self.y_size

        x_dist = x_pixels_from_center * self.size_per_gap
        y_dist = y_pixels_from_center * self.size_per_gap

        return self.centre + x_dist*self.x_unit + y_dist*self.y_unit

    def get_source_point_from_complex(self, z: complex) -> Optional[tuples.PixelPoint]:
        dz = z - self.centre

        # take dot products
        x_dist = dz.real*self.x_unit.real + dz.imag*self.x_unit.imag
        y_dist = dz.real*self.y_unit.real + dz.imag*self.y_unit.imag

        x_pixels_from_center = x_dist/self.size_per_gap
        y_pixels_from_center = y_dist/self.size_per_gap

        x_pixel = 0.5*float(self.shape.x-1) + x_pixels_from_center
        y_pixel = 0.5*float(self.shape.y-1) + y_pixels_from_center

        x = round(x_pixel)
        y = round(y_pixel)

        if 0 <= x <= self.shape.x-1 and 0 <= y <= self.shape.y-1:
            return tuples.PixelPoint(x, y)
        else:
            return None

        # x_scale = x_dist / self.x_size
        # y_scale = y_dist / self.y_size
        #
        # if -0.5 <= x_scale <= 0.5 and -0.5 <= y_scale <= 0.5:
        #     x_pixel = (x_scale + 0.5) * float(self.shape.x-1)
        #     y_pixel = (y_scale + 0.5) * float(self.shape.y-1)
        #     source_point = tuples.PixelPoint(
        #         x=round(x_pixel),
        #         y=round(y_pixel)
        #     )
        #     return source_point
        # else:
        #     return None

    # def set_offset(self, offset: tuples.PixelPoint):
    #     """happens when window is resized"""
    #     # noinspection PyAttributeOutsideInit
    #     self.offset = offset
    # endregion

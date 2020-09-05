from typing import Optional, List, Callable

import numpy as np
from matplotlib import lines, cm, colors

from mandel_app import tuples
from mandel_app.model import mandelbrot
from mandel_app.view import portal


class DrawMandelFrame(portal.Drawable):
    def __init__(self):
        super().__init__()
        # self._z0: Optional[complex] = None
        self._frame_shape: Optional[tuples.ImageShape] = None
        self._z0_source_point: Optional[tuples.PixelPoint] = None
        self._complex_to_source: Optional[Callable[[complex], tuples.PixelPoint]] = None
        self._source_to_transformed_frame: Optional[Callable[[tuples.PixelPoint], tuples.PixelPoint]] = None

        # self._z0_frame_point: Optional[tuples.PixelPoint] = None
        self._z0_marker = lines.Line2D([], [], marker='x', markersize=30, color="blue",
                                       zorder=1, visible=False)

    @property
    def shape(self) -> Optional[tuples.ImageShape]:
        return self._frame_shape

    # either store and update this function when mandel changes, or have a fresh source point calculated and passed in
    # would still need z0 passed in again
    # unless could get a link back to z0, perhaps another callback function
    # is this getting too messy? But what if wanted to update many things here which depended on z-values
    # def set_complex_to_source(self,
    #                           complex_to_source: Callable[[complex], tuples.PixelPoint]):
    #     self._complex_to_source = complex_to_source
    #
    # def set_z0(self, z0: complex):
    #     self._z0_source_point = self._complex_to_source(z0)
    #     self.show_z0()

    # rather than storing a pointer to frame or portal, just store the transform function
    # this link is set at the start and never changes
    def set_source_to_transformed_frame(self,
                                        source_to_transformed_frame: Callable[[tuples.PixelPoint], tuples.PixelPoint]):
        self._source_to_transformed_frame = source_to_transformed_frame

    def set_frame_shape(self, frame_shape: tuples.ImageShape):
        self._frame_shape = frame_shape

    def set_z0_source_point(self, z0_source_point: tuples.PixelPoint):
        # print("set_z0_source_point")
        # print(f"z0_source_point: {z0_source_point}")
        self._z0_source_point = z0_source_point
        self.show_z0()
        # self._set_z0_frame_point()

    # def _set_z0_frame_point(self):
    #     self._z0_frame_point = tuples.PixelPoint(400, 200)
    #     # self._z0_frame_point = self._mandel.get_source_point_from_complex(z0)
    #     if self._z0_frame_point is None:
    #         self._z0_marker.set_visible(False)
    #     else:
    #         self._z0_marker.set_data([self._z0_frame_point.x], [self._z0_frame_point.y])
    #         self._z0_marker.set_visible(True)

    def hide_z0(self):
        self._z0_marker.set_visible(False)

    def show_z0(self):
        self._z0_marker.set_visible(True)

    def draw(self):
        if self._z0_source_point is not None and self._z0_marker.get_visible():
            frame_point = self._source_to_transformed_frame(self._z0_source_point)
            # print(f"z0_frame_point: {frame_point}")
            self._z0_marker.set_data([frame_point.x], [frame_point.y])
            self._ax.draw_artist(self._z0_marker)

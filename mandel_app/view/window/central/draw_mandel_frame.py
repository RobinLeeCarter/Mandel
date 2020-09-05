from typing import Optional, List

import numpy as np
from matplotlib import lines, cm, colors

from mandel_app import tuples
from mandel_app.model import mandelbrot
from mandel_app.view import portal


class DrawMandelFrame(portal.Drawable):
    def __init__(self):
        super().__init__()
        self._z0: Optional[complex] = None
        self._frame_shape: Optional[tuples.ImageShape] = None

        self._z0_frame_point: Optional[tuples.PixelPoint] = None
        self._z0_marker = lines.Line2D([], [], marker='x', markersize=30, color="blue",
                                       zorder=1, visible=False)

    @property
    def shape(self) -> Optional[tuples.ImageShape]:
        return self._frame_shape

    def set_frame_shape(self, frame_shape: tuples.ImageShape):
        self._frame_shape = frame_shape

    @property
    def z0(self) -> Optional[complex]:
        return self._z0

    def set_z0(self, z0: complex):
        self._z0 = z0
        self._set_z0_frame_point()

    def _set_z0_frame_point(self):
        self._z0_frame_point = tuples.PixelPoint(400, 200)
        # self._z0_frame_point = self._mandel.get_source_point_from_complex(z0)
        if self._z0_frame_point is None:
            self._z0_marker.set_visible(False)
        else:
            self._z0_marker.set_data([self._z0_frame_point.x], [self._z0_frame_point.y])
            self._z0_marker.set_visible(True)

    def hide_z0(self):
        self._z0_marker.set_visible(False)

    def show_z0(self):
        self._z0_marker.set_visible(True)

    def draw(self):
        if self._z0_frame_point is not None and self._z0_marker.get_visible():
            self._ax.draw_artist(self._z0_marker)

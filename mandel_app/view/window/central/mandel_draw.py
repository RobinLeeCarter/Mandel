from typing import Optional, List

import numpy as np
from matplotlib import figure, backend_bases, image, transforms, lines, cm, colors

from mandel_app import tuples
from mandel_app.model import mandelbrot
from mandel_app.view import portal


class MandelDraw(portal.Drawable):
    def __init__(self):
        super().__init__()
        self._mandel: Optional[mandelbrot.Mandel] = None
        self._cmap = cm.get_cmap("hot")
        self._norm = colors.Normalize(vmin=0, vmax=1)
        self._transformed_iterations: Optional[np.ndarray] = None
        self._z0: Optional[complex] = None  # TODO: Remove and use mandel directly
        self._z0_marker = lines.Line2D([], [], marker='x', markersize=30, color="blue",
                                       zorder=1, visible=False)

    @property
    def mandel(self) -> Optional[mandelbrot.Mandel]:
        return self._mandel

    def set_mandel(self, mandel_: mandelbrot.Mandel):
        self._mandel = mandel_
        self._transformed_iterations = np.mod(np.log10(1 + self._mandel.iteration), 1)
        self._transformed_iterations[self._mandel.iteration == self._mandel.max_iteration] = 0
        self._adopt_shape(self._transformed_iterations)

    def draw(self):
        assert self._mandel is not None, "MandelDraw: mandel is None"
        self._ax.set_axis_off()
        self._ax.margins(0, 0)
        self._ax.imshow(
            self._transformed_iterations,
            interpolation='none', origin='lower',
            cmap=self._cmap, norm=self._norm, resample=False, filternorm=False)  # , zorder=0
        self._ax.add_line(self._z0_marker)
        if self._z0 is not None:
            self._set_z0_marker()

    def show_z0_marker(self, z0: complex):
        self._z0 = z0
        self._set_z0_marker()
        self.figure_canvas.draw()

    def _set_z0_marker(self):
        pixel_x: List[int] = []
        pixel_y: List[int] = []
        pixel_point: Optional[tuples.PixelPoint] = self._mandel.get_pixel_from_complex(self._z0)
        if pixel_point is not None:
            pixel_x.append(pixel_point.x)
            pixel_y.append(pixel_point.y)
            # self._z0_marker.set_data([pixel_point.x], [pixel_point.y])
        self._z0_marker.set_data(pixel_x, pixel_y)
        self._z0_marker.set_visible(True)

    def hide_z0_marker(self):
        self._z0 = None
        self._z0_marker.set_visible(False)
        self.figure_canvas.draw()

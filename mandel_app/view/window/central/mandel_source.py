from typing import Optional, List

import numpy as np
from matplotlib import lines, cm, colors

from mandel_app import tuples
from mandel_app.model import mandelbrot
from mandel_app.view import portal


class MandelSource(portal.Drawable):
    def __init__(self):
        super().__init__()
        self._mandel: Optional[mandelbrot.Mandel] = None
        self._cmap = cm.get_cmap("hot")
        self._norm = colors.Normalize(vmin=0, vmax=1)
        self._transformed_iterations: Optional[np.ndarray] = None

        self._z0_source_point: Optional[tuples.PixelPoint] = None
        self._z0_marker = lines.Line2D([], [], marker='x', markersize=30, color="blue",
                                       zorder=1, visible=False)

    @property
    def shape(self) -> Optional[tuples.ImageShape]:
        if self._transformed_iterations is None:
            return None
        else:
            return self._get_shape(self._transformed_iterations)

    # @property
    # def offset(self) -> Optional[tuples.PixelPoint]:
    #     if self._mandel is None:
    #         return None
    #     else:
    #         return self._mandel.offset

    @property
    def mandel(self) -> Optional[mandelbrot.Mandel]:
        return self._mandel

    def set_mandel(self, mandel_: mandelbrot.Mandel):
        self._mandel = mandel_
        self._transformed_iterations = np.mod(np.log10(1 + self._mandel.iteration), 1)
        self._transformed_iterations[self._mandel.iteration == self._mandel.max_iteration] = 0
        # self._adopt_shape(self._transformed_iterations)
        # self.offset = self._mandel.offset

    def set_cmap(self, cmap: colors.Colormap):
        self._cmap = cmap

    def draw(self):
        assert self._mandel is not None, "MandelSource: mandel is None"
        self._ax.set_axis_off()
        self._ax.margins(0, 0)
        self._ax.imshow(
            self._transformed_iterations,
            interpolation='none', origin='lower',
            cmap=self._cmap, norm=self._norm, resample=False, filternorm=False)  # , zorder=0
        if self._z0_source_point is not None:
            self._ax.add_line(self._z0_marker)

    # def update(self):
    #     """Maybe extend to use animation in future"""
    #     self.draw()

    # def show_z0_marker(self, z0: complex):
    #     self._set_z0_marker(z0)
    #     # self.figure_canvas.draw()

    def set_z0_marker(self, z0: complex):
        pixel_x: List[int] = []
        pixel_y: List[int] = []
        self._z0_source_point = self._mandel.get_source_point_from_complex(z0)
        if self._z0_source_point is not None:
            pixel_x.append(self._z0_source_point.x)
            pixel_y.append(self._z0_source_point.y)
            # self._z0_marker.set_data([pixel_point.x], [pixel_point.y])
        self._z0_marker.set_data(pixel_x, pixel_y)
        self._z0_marker.set_visible(True)

    def hide_z0_marker(self):
        self._z0_source_point = None
        self._z0_marker.set_visible(False)
        # self.figure_canvas.draw()

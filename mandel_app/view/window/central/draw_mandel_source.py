from typing import Optional

import numpy as np
from matplotlib import lines, cm, colors

from mandel_app import tuples
from mandel_app.model import mandelbrot
from mandel_app.view import portal


class DrawMandelSource(portal.Drawable):
    def __init__(self):
        super().__init__()
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

    def set_mandel(self, mandel: mandelbrot.Mandel):
        self._transformed_iterations = np.mod(np.log10(1 + mandel.iteration), 1)
        self._transformed_iterations[mandel.iteration == mandel.max_iteration] = 0

    def set_cmap(self, cmap: colors.Colormap):
        self._cmap = cmap

    def draw(self):
        self._ax.clear()
        self._ax.set_axis_off()
        self._ax.margins(0, 0)
        self._ax.autoscale(False)
        self._ax.set_xlim(xmin=0, xmax=self.shape.x - 1)
        self._ax.set_ylim(ymin=0, ymax=self.shape.y - 1)
        self._ax.imshow(
            self._transformed_iterations,
            interpolation='none', origin='lower',
            cmap=self._cmap, norm=self._norm, resample=False, filternorm=False)  # , zorder=0

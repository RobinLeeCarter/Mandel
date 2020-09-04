from __future__ import annotations

from typing import Optional

import numpy as np

from matplotlib import figure
from matplotlib.backends import backend_qt5agg

# import utils
from mandel_app import tuples
from mandel_app.view.portal import drawable


class Canvas:
    """
    Renders a single axes to an rgba array.
    Does not need to be physically displayed on the screen but canvas.draw() still required.
    0.1s slower than direct input array to rgba array (using cmap) but thought to be worth it for consistency.
    """
    def __init__(self):
        self._fig: figure.Figure = figure.Figure(frameon=False, dpi=100.0)
        self._figure_canvas: backend_qt5agg.FigureCanvasQTAgg = backend_qt5agg.FigureCanvasQTAgg(self._fig)
        # Space around axes. Documentation not helpful. Taken from stack-overflow.
        self._fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        self._ax: figure.Axes = self._fig.subplots()
        self._drawable: Optional[drawable.Drawable] = None
        self._rgba_output: Optional[np.ndarray] = None

        # self._timer = utils.Timer()

    @property
    def shape(self) -> tuples.ImageShape:
        return self._drawable.shape

    @property
    def rgba_output(self) -> np.ndarray:
        assert self._rgba_output is not None, "Canvas: _rgba is None"
        return self._rgba_output

    def set_drawable(self, drawable_: drawable.Drawable):
        self._drawable = drawable_
        self._set_drawable_ax()

    def _set_drawable_ax(self):
        self._drawable.set_ax(self._ax)

    def draw(self):
        # Get fig ready
        self._set_fig_size()

        # Get ax ready
        self._ax.clear()

        # Compose ax
        assert self._drawable is not None, "Canvas: No drawable set"
        self._drawable.draw()

        # Draw off-screen and get RGBA array
        # https://matplotlib.org/gallery/user_interfaces/canvasagg.html#sphx-glr-gallery-user-interfaces-canvasagg-py
        self._figure_canvas.draw()
        buf: memoryview = self._figure_canvas.buffer_rgba()
        self._rgba_output = np.asarray(buf)

    def _set_fig_size(self):
        width, height = self.shape
        width_inches: float = float(width) / 100.0
        height_inches: float = float(height) / 100.0
        self._fig.set_size_inches(width_inches, height_inches)
        # self._figure_canvas.resize(self._width, self._height)

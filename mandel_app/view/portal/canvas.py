from __future__ import annotations

from typing import Optional

import numpy as np

from matplotlib import figure
from matplotlib.backends import backend_qt5agg

import utils
from mandel_app import tuples
from mandel_app.view.portal import drawable


class Canvas:
    """
    Renders a single axes to an rgba array.
    Does not need to be physically displayed on the screen but canvase.draw() still required.
    0.1s slower than direct input array to rgba array but thought to be worth it for consistency.
    """
    def __init__(self):
        self._fig: figure.Figure = figure.Figure(frameon=False, dpi=100.0)
        self._figure_canvas: backend_qt5agg.FigureCanvasQTAgg = backend_qt5agg.FigureCanvasQTAgg(self._fig)
        # Space around axes. Documentation not helpful. Taken from stack-overflow.
        self._fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        self._ax: figure.Axes = self._fig.subplots()
        self._drawable: Optional[drawable.Drawable] = None
        self._rgba: Optional[np.ndarray] = None

        # self._figure_canvas.draw()
        self._timer = utils.Timer()

    @property
    def shape(self) -> tuples.ImageShape:
        return self._drawable.shape

    @property
    def offset(self) -> tuples.PixelPoint:
        return self._drawable.offset

    @property
    def rgba(self) -> np.ndarray:
        assert self._rgba is not None, "Canvas: _rgba is None"
        return self._rgba

    def set_drawable(self, drawable_: drawable.Drawable):
        self._drawable = drawable_
        self._drawable.set_ax(self._ax)

    def draw(self, drawable_: Optional[drawable.Drawable] = None) -> np.ndarray:
        if drawable_ is not None:
            self.set_drawable(drawable_)
        assert self._drawable is not None, "Canvas: No drawable set"

        # Get fig ready
        width, height = self.shape
        width_inches: float = float(width) / 100.0
        height_inches: float = float(height) / 100.0
        self._fig.set_size_inches(width_inches, height_inches)
        # self._figure_canvas.resize(self._width, self._height)

        # Get ax ready
        self._ax.clear()

        # Compose ax
        self._drawable.draw()

        # Draw off-screen and get RGBA array
        # https://matplotlib.org/gallery/user_interfaces/canvasagg.html#sphx-glr-gallery-user-interfaces-canvasagg-py
        self._figure_canvas.draw()
        buf: memoryview = self._figure_canvas.buffer_rgba()
        self._rgba = np.asarray(buf)

        return self.rgba

        # alternative : https://matplotlib.org/3.1.1/gallery/user_interfaces/canvasagg.html
        # s, (width, height) = self._figure_canvas.print_to_buffer()
        # graph_rgba = np.frombuffer(s, np.uint8).reshape((height, width, 4))

        # direct_rgba = cmap(normalised)

    # @property
    # def figure_canvas(self) -> backend_qt5agg.FigureCanvasQTAgg:
    #     return self._figure_canvas

#        data = self.make_data(mid_x=0.5, mid_y=0.4, width=self._width, height=self._height)

from __future__ import annotations

from typing import Optional

import numpy as np

from matplotlib import figure
from matplotlib.backends import backend_qt5agg

# import utils
from mandel_app import tuples
from mandel_app.view.portal import drawable, canvas_base


class CanvasSource(canvas_base.CanvasBase):
    """
    Renders a single axes to an rgba array.
    Does not need to be physically displayed on the screen but canvas.draw() still required.
    0.1s slower than direct input array to rgba array (using cmap) but thought to be worth it for consistency.
    """
    def __init__(self):
        super().__init__()
        # self._timer = utils.Timer()

    def _set_drawable_ax(self):
        self._drawable.set_ax(self._ax)

    def draw(self):
        # Get fig ready
        self._set_fig_size()

        # Get ax ready
        self._ax.clear()

        # Compose ax
        assert self._drawable is not None, "Canvas: No drawable set"
        self._drawable.draw_source()

        # Draw off-screen and get RGBA array
        # https://matplotlib.org/gallery/user_interfaces/canvasagg.html#sphx-glr-gallery-user-interfaces-canvasagg-py
        self._figure_canvas.draw()
        buf: memoryview = self._figure_canvas.buffer_rgba()
        self._rgba_output = np.asarray(buf)

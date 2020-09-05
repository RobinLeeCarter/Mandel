from __future__ import annotations

import numpy as np

from mandel_app.view.portal import canvas_base


class CanvasSource(canvas_base.CanvasBase):
    """
    Renders a single axes to an rgba array.
    Does not need to be physically displayed on the screen but canvas.draw() still required.
    0.1s slower than direct input array to rgba array (using cmap) but thought to be worth it for consistency.
    """
    def __init__(self):
        super().__init__()
        self.first_draw: bool = True
        # self._timer = utils.Timer()

    def draw(self):
        # Get fig ready
        self._fig_size()

        # Compose ax
        assert self._drawable is not None, "Canvas: No drawable set"
        self._drawable.draw()

        # Draw off-screen and get RGBA array
        # https://matplotlib.org/gallery/user_interfaces/canvasagg.html#sphx-glr-gallery-user-interfaces-canvasagg-py
        self._figure_canvas.draw()
        self._buf: memoryview = self._figure_canvas.buffer_rgba()
        # print(self._buf)
        self._rgba_output = np.asarray(self._buf)

from __future__ import annotations

from typing import Optional

import numpy as np

from matplotlib import figure
from matplotlib.backends import backend_qt5agg

# import utils
from mandel_app import tuples
from mandel_app.view.portal import drawable, canvas_base


class CanvasFrame(canvas_base.CanvasBase):
    """
    Renders a single axes to an rgba array.
    Does not need to be physically displayed on the screen but canvas.draw() still required.
    0.1s slower than direct input array to rgba array (using cmap) but thought to be worth it for consistency.
    """
    def __init__(self):
        super().__init__()
        self._rgba_input: Optional[np.ndarray] = None
        # self._timer = utils.Timer()

    def _on_resize(self):
        super()._on_resize()
        self._ax.clear()
        self._ax.set_axis_off()
        self._ax.margins(0, 0)
        self._figure_canvas.draw()

        print(f"self._rgba_output.shape: {self._rgba_output.shape}")
        print(f"self._rgba_output.dtype: {self._rgba_output.dtype}")

    # def set_frame_shape(self, frame_shape: tuples.ImageShape):
    #     self._drawable.set_frame_shape(frame_shape)

    def set_rgba_input(self, rgba_input: np.ndarray):
        self._rgba_input = rgba_input

    def draw(self):
        # Get fig ready
        self._fig_size()

        self._buf = self._figure_canvas.buffer_rgba()
        self._rgba_output = np.asarray(self._buf)

        if self._rgba_input is not None:
            np.copyto(dst=self._rgba_output, src=self._rgba_input)

        # Get ax ready
        # self._ax.clear()
        # self._ax.set_axis_off()
        # self._ax.margins(0, 0)

        # Compose ax
        assert self._drawable is not None, "CanvasFrame: No drawable set"
        self._drawable.draw()

        # self._rgba_output should now be updated
        # might need:
        # self._buf = self._figure_canvas.buffer_rgba()
        # self._rgba_output = np.asarray(self._buf)

        # Draw off-screen and get RGBA array
        # https://matplotlib.org/gallery/user_interfaces/canvasagg.html#sphx-glr-gallery-user-interfaces-canvasagg-py
        # self._figure_canvas.draw()
        # self._buf: memoryview = self._figure_canvas.buffer_rgba()
        # self._rgba_output = np.asarray(self._buf)

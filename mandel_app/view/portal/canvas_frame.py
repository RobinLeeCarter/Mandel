from __future__ import annotations

from typing import Optional

import numpy as np

from mandel_app.view.portal import canvas_base
# import utils


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
        self._ax.autoscale(False)
        self._ax.set_xlim(xmin=0, xmax=self.shape.x - 1)
        self._ax.set_ylim(ymin=0, ymax=self.shape.y - 1)
        self._figure_canvas.draw()

    def set_rgba_input(self, rgba_input: np.ndarray):
        self._rgba_input = rgba_input

    def draw(self):
        # Get fig ready
        self._fig_size()

        # Draw off-screen and get RGBA array
        # https://matplotlib.org/gallery/user_interfaces/canvasagg.html#sphx-glr-gallery-user-interfaces-canvasagg-py
        self._buf = self._figure_canvas.buffer_rgba()
        self._rgba_output = np.asarray(self._buf)
        # print(f"self._drawable.shape:\t{self._drawable.shape}")
        # print(f"CanvasFrame._rgba_output:\t{self._rgba_output.shape}")
        # print(f"CanvasFrame._rgba_input:\t{self._rgba_input.shape}")

        if self._rgba_input is not None:
            if self._rgba_output.shape == self._rgba_input.shape:
                np.copyto(dst=self._rgba_output, src=self._rgba_input)
            else:
                # very occasionally self._rgba_output.shape is the wrong shape by 1 pixel (!= self._drawable.shape)
                # this copy process is almost instant 0.001s or less
                min_y = min(self._rgba_input.shape[0], self._rgba_output.shape[0])
                min_x = min(self._rgba_input.shape[1], self._rgba_output.shape[1])
                self._rgba_output[:, :, :] = 0
                self._rgba_output[0:min_y, 0:min_x, :] = self._rgba_input[0:min_y, 0:min_x, :]

        # Compose ax
        assert self._drawable is not None, "CanvasFrame: No drawable set"
        self._drawable.draw()

        # self._figure_canvas.blit(self._ax.bbox)

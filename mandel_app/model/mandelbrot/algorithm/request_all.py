from __future__ import annotations

import numpy as np

from mandel_app import tuples

from mandel_app.model.mandelbrot.server import server


class RequestAll:

    def __init__(self, server_: server.Server, shape: tuples.ImageShape):
        self.server = server_
        self.shape = shape

    def run(self) -> np.ndarray:
        bottom_left = tuples.PixelPoint(0, 0)
        top_right = tuples.PixelPoint(x=self.shape.x, y=self.shape.y)
        self.server.box_request(bottom_left, top_right)
        self.server.serve()
        return self.server.iteration_cpu

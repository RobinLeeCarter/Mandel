from __future__ import annotations

from typing import Optional, Generator

import numpy as np

# import utils
from mandel_app import tuples
from mandel_app.model.mandelbrot import server, mandel_progress_estimator


class Mesh:

    def __init__(self, server_: server.Server, progress_estimator: mandel_progress_estimator.MandelProgressEstimator):
        self.server: server.Server = server_
        self.progress_estimator: mandel_progress_estimator.MandelProgressEstimator = progress_estimator
        self.shape: tuples.ImageShape = server_.shape
        self.iteration: Optional[np.ndarray] = None

        self.mesh_step: int = 0
        self.v_slice_max: int = 0
        self.h_slice_max: int = 0
        self.v_value: Optional[np.ndarray] = None
        self.v_same: Optional[np.ndarray] = None
        self.h_value: Optional[np.ndarray] = None
        self.h_same: Optional[np.ndarray] = None
        self.box_value: Optional[np.ndarray] = None
        self.box_same: Optional[np.ndarray] = None

        # self._timer = utils.Timer()

    def run(self) -> Generator[float, None, np.ndarray]:
        base_size = 14
        if self.progress_estimator:
            self.progress_estimator.set_progress_range(progress_to=1.0, mode="WORK")

        yield from self._do_mesh(base_size * 4)
        yield from self._do_mesh(base_size)
        yield from self._do_remainder()
        return self.iteration

    def _do_mesh(self, mesh_step: int) -> Generator[float, None, None]:
        self.mesh_step = mesh_step
        self.v_slice_max = self.mesh_step * int(self.shape[1] / self.mesh_step)
        self.h_slice_max = self.mesh_step * int(self.shape[0] / self.mesh_step)

        # self._timer.lap(f"start {self.mesh_step}\t")
        self.server.grid_lines_request(self.mesh_step)
        # self._timer.lap("request  \t")
        yield from self.server.serve()
        # self._timer.lap("serve    \t")

        self.iteration = self.server.iteration_cpu
        # self._timer.lap("retrieve \t")
        self._verticals()
        self._horizontals()
        # self._timer.lap("vert/hori\t")
        self._check_boxes()
        # self._timer.lap("do check \t")
        self._fill_boxes()
        # self._timer.lap("do fill  \t")

    def _do_remainder(self) -> Generator[float, None, None]:
        # self._timer.lap(f"remainder\t")
        self.server.request_incomplete()
        # self._timer.lap("request  \t")
        yield from self.server.serve()
        # self._timer.lap("serve    \t")
        self.iteration = self.server.iteration_cpu
        # self._timer.lap("retrieve \t")
        # self._timer.stop()

    def _verticals(self):
        vertical_slices_2d: np.ndarray = self.iteration[:self.v_slice_max, ::self.mesh_step]
        slices: int = vertical_slices_2d.shape[1]
        chunk_up_3d = vertical_slices_2d.reshape((-1, self.mesh_step, slices))
        self.v_value: np.ndarray = chunk_up_3d[:, 0, :]
        self.v_same: np.ndarray = np.all(
            (chunk_up_3d == np.expand_dims(self.v_value, axis=1)),
            axis=1)

    def _horizontals(self):
        horizontal_slices_2d: np.ndarray = self.iteration[::self.mesh_step, :self.h_slice_max]
        slices: int = horizontal_slices_2d.shape[0]
        chunk_up_3d = horizontal_slices_2d.reshape((slices, -1, self.mesh_step))
        self.h_value: np.ndarray = chunk_up_3d[:, :, 0]
        self.h_same: np.ndarray = np.all(
            (chunk_up_3d == np.expand_dims(self.h_value, axis=2)),
            axis=2)

    def _check_boxes(self):
        rows = self.h_value.shape[0] - 1
        cols = self.v_value.shape[1] - 1
        self.box_value = np.zeros(shape=(rows, cols), dtype=np.int)
        self.box_same = np.zeros(shape=(rows, cols), dtype=np.bool)
        for row in range(rows):
            for col in range(cols):
                self._check_box(row, col)

    def _check_box(self, row: int, col: int):
        if self.v_same[row, col] and self.v_same[row, col + 1] and self.h_same[row, col] and self.h_same[row + 1, col]:
            # left edge value:
            value = self.v_value[row, col]
            # bottom edge: self.h_value[row, col] must be the same value since they are taken from the same pixel
            # test right edge and top edge have the same value
            if self.v_value[row, col+1] == value and self.h_value[row+1, col] == value:
                # finally test top right pixel is the same value (relevant edges might not exist)
                if self.iteration[(row + 1) * self.mesh_step, (col + 1) * self.mesh_step] == value:
                    self.box_same[row, col] = True
                    self.box_value[row, col] = value

    def _fill_boxes(self):
        rows, cols = self.box_value.shape
        for row in range(rows):
            for col in range(cols):
                if self.box_same[row, col]:
                    # define inside of box
                    bottom_left = tuples.PixelPoint(
                        x=col*self.mesh_step + 1,
                        y=row*self.mesh_step + 1
                    )
                    top_right = tuples.PixelPoint(
                        x=(col+1)*self.mesh_step - 1,
                        y=(row+1)*self.mesh_step - 1
                    )
                    self.server.fill_box_request(bottom_left, top_right, self.box_value[row, col])

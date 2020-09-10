from __future__ import annotations

from typing import Optional, Callable, List, Generator

import numpy as np
import cupy as cp

from mandel_app import tuples

from mandel_app.model.mandelbrot import mandel, compute  # mandel_progress_estimator
from mandel_app.model.mandelbrot.server import request


# generate one for each mandel calculation
# serves requests for mandel pixel calculations
# compute does the actual calculation
class Server:

    # region Setup
    def __init__(self,
                 compute_manager_: compute.ComputeManager,
                 new_mandel: mandel.Mandel,
                 early_stopping_iteration: Optional[int] = None,
                 prev_mandel: Optional[mandel.Mandel] = None,
                 offset: Optional[tuples.PixelPoint] = None
                 ):
        self._compute_manager: compute.ComputeManager = compute_manager_
        self._new_mandel: mandel.Mandel = new_mandel
        self._early_stopping_iteration: Optional[int] = early_stopping_iteration
        self._prev_mandel: Optional[mandel.Mandel] = prev_mandel
        # offset vector from prev_mandel origin to new_mandel origin (this already includes any pan)
        self._offset: Optional[tuples.PixelPoint] = offset

        # removed
        # if self._mandel.pan is not None:
        #     self._mandel.pan_centre()

        shape = (self._new_mandel.shape.y, self._new_mandel.shape.x)

        # self._c: cp.ndarray = self._generate_c()

        self._iteration: cp.ndarray = cp.zeros(shape=shape, dtype=cp.int32)
        self._completed: cp.ndarray = cp.zeros(shape=shape, dtype=cp.bool)

        self._requested: cp.ndarray = cp.zeros(shape=shape, dtype=cp.bool)
        self._requests: List[request.Request] = []

        self._box_fills: bool = False
        self._box_iter_cpu: np.ndarray = np.zeros(shape=shape, dtype=np.int32)
        self._box_fill_cpu: np.ndarray = np.zeros(shape=shape, dtype=np.bool)

        self._c: cp.ndarray = cp.zeros(shape=shape, dtype=cp.float64)

        self._build()

    def _build(self):
        self._c: cp.ndarray = self._generate_c()

        if self._prev_mandel is not None and self._offset is not None:
            self._copy_over_prev()
        # if self._new_mandel.pan is not None:
        #     self._copy_over_pan()
        # self._new_mandel.pan = None
        #
        # if self._new_mandel.has_border:
        #     self._copy_over_center()

    def _generate_c(self) -> cp.ndarray:
        """Found to be faster using numpy, ogrid presumably not possible to parallelize."""
        m = self._new_mandel
        y, x = np.ogrid[-m.y_size/2.0: m.y_size/2.0: m.shape.y * 1j,
                        -m.x_size/2.0: m.x_size/2.0: m.shape.x * 1j]

        # y, x = np.ogrid[0: m.y_size: m.shape.y * 1j,
        #                 0: m.x_size: m.shape.x * 1j]

        # print("m.shape.y", m.shape.y)
        # print("m.y_size", m.y_size)
        # print("m.size_per_gap", m.size_per_gap)

        # print("self._mandel.size", self._mandel.size)
        # print("self._mandel.size_per_thousand", self._mandel.size_per_thousand)
        # if not self._mandel.has_border:
        #     print("y[0] = ", y[0])
        # else:
        #     print("y[56] = ", y[56])
        #     estimate = ((m.y_size / 1019) * 56) - (m.y_size/2.0)
        #     print("est   = ", estimate)

        c = m.centre + x*m.x_unit + y*m.y_unit

        return cp.asarray(c)

    def _copy_over_prev(self):
        new = self._new_mandel.shape
        prev = self._prev_mandel.shape
        offset = self._offset
        # print("\n")
        # print(f"prev center: {self._prev_mandel.centre}")
        # print(f"new center: {self._new_mandel.centre}")
        # print(f"prev shape: {prev}")
        # print(f"new shape : {new}")
        # print(f"offset    : {offset}")

        prev_slice_x: Optional[slice] = None
        new_slice_x: Optional[slice] = None
        prev_slice_y: Optional[slice] = None
        new_slice_y: Optional[slice] = None

        # x
        prev_start_x = None
        prev_stop_x = None
        if offset.x >= 0:
            # new to right of prev
            if offset.x < prev.x:
                # overlap
                prev_start_x = offset.x
                prev_stop_x = min(prev.x, new.x + offset.x)
        else:
            # new to left of prev
            if -offset.x < new.x:
                # overlap
                prev_start_x = 0
                prev_stop_x = min(prev.x, new.x + offset.x)
        if prev_start_x is not None:
            new_start_x = prev_start_x - offset.x
            new_stop_x = prev_stop_x - offset.x
            prev_slice_x = slice(prev_start_x, prev_stop_x)
            new_slice_x = slice(new_start_x, new_stop_x)

        # y
        prev_start_y = None
        prev_stop_y = None
        if offset.y >= 0:
            # new above prev
            if offset.y < prev.y:
                # overlap
                prev_start_y = offset.y
                prev_stop_y = min(prev.y, new.y + offset.y)
        else:
            # new below prev
            if -offset.y < new.y:
                # overlap
                prev_start_y = 0
                prev_stop_y = min(prev.y, new.y + offset.y)
        if prev_start_y is not None:
            new_start_y = prev_start_y - offset.y
            new_stop_y = prev_stop_y - offset.y
            prev_slice_y = slice(prev_start_y, prev_stop_y)
            new_slice_y = slice(new_start_y, new_stop_y)

        if prev_start_x is not None and prev_start_y is not None:
            # there is some overlap, so copy over and mark as completed
            # print(f"prev_slice_x: {prev_slice_x}")
            # print(f"prev_slice_y: {prev_slice_y}")
            # print(f"new_slice_x : {new_slice_x}")
            # print(f"new_slice_y : {new_slice_y}")

            prev_iteration = cp.asarray(self._prev_mandel.iteration)
            self._iteration[new_slice_y, new_slice_x] = prev_iteration[prev_slice_y, prev_slice_x]
            self._completed[new_slice_y, new_slice_x] = True
    # endregion

    # def _copy_over_pan(self):
    #     new = self._new_mandel.shape
    #     old = self._new_mandel.iteration_shape
    #     offset = self._new_mandel.iteration_offset
    #     pan = self._new_mandel.pan
    #
    #     bottom_left: tuples.PixelPoint = tuples.PixelPoint(x=pan.x - offset.x,
    #                                                        y=pan.y - offset.y)
    #     top_right: tuples.PixelPoint = tuples.PixelPoint(x=bottom_left.x + new.x,
    #                                                      y=bottom_left.y + new.y)
    #
    #     if bottom_left.x <= 0:      # outside to left
    #         old_start_x = 0
    #         new_start_x = -bottom_left.x
    #     else:
    #         old_start_x = bottom_left.x
    #         new_start_x = 0
    #
    #     if top_right.x >= old.x:    # outside to right
    #         old_end_x = old.x
    #         new_end_x = old.x - bottom_left.x
    #     else:
    #         old_end_x = top_right.x
    #         new_end_x = new.x
    #     x_old_slice = slice(old_start_x, old_end_x)
    #     x_new_slice = slice(new_start_x, new_end_x)
    #
    #     if bottom_left.y <= 0:      # outside below
    #         old_start_y = 0
    #         new_start_y = -bottom_left.y
    #     else:
    #         old_start_y = bottom_left.y
    #         new_start_y = 0
    #
    #     if top_right.y >= old.y:    # outside above
    #         old_end_y = old.y
    #         new_end_y = old.y - bottom_left.y
    #     else:
    #         old_end_y = top_right.y
    #         new_end_y = new.y
    #     y_old_slice = slice(old_start_y, old_end_y)
    #     y_new_slice = slice(new_start_y, new_end_y)
    #
    #     old_iteration = cp.asarray(self._new_mandel.iteration)
    #     self._iteration[y_new_slice, x_new_slice] = old_iteration[y_old_slice, x_old_slice]
    #     self._completed[y_new_slice, x_new_slice] = True
    #
    # def _copy_over_center(self):
    #     old = self._new_mandel.iteration_shape
    #     offset = self._new_mandel.offset
    #
    #     bottom_left: tuples.PixelPoint = tuples.PixelPoint(x=-offset.x,
    #                                                        y=-offset.y)
    #     top_right: tuples.PixelPoint = tuples.PixelPoint(x=bottom_left.x + old.x,
    #                                                      y=bottom_left.y + old.y)
    #
    #     x_old_slice = slice(0, old.x)
    #     x_new_slice = slice(bottom_left.x, top_right.x)
    #     y_old_slice = slice(0, old.y)
    #     y_new_slice = slice(bottom_left.y, top_right.y)
    #
    #     old_iteration = cp.asarray(self._new_mandel.iteration)
    #     self._iteration[y_new_slice, x_new_slice] = old_iteration[y_old_slice, x_old_slice]
    #     self._completed[y_new_slice, x_new_slice] = True

    @property
    def shape(self) -> tuples.ImageShape:
        return self._new_mandel.shape

    @property
    def complete(self) -> bool:
        return self._completed.all()

    @property
    def new_request_count(self) -> int:
        return int(cp.count_nonzero(self._requested & ~self._completed))

    @property
    def iteration(self) -> cp.ndarray:
        return self._iteration

    @property
    def iteration_cpu(self) -> np.ndarray:
        return cp.asnumpy(self._iteration)

    @property
    def c_cpu(self) -> np.ndarray:
        return cp.asnumpy(self._c)

    # TODO: implemented for flatten
    def compute_flat_array(self, gpu_c_flat: cp.ndarray) -> cp.ndarray:
        raise NotImplementedError

    # requests are for pixels (inclusive). They know nothing of complex numbers
    def box_request(
            self,
            bottom_left: tuples.PixelPoint,
            top_right: tuples.PixelPoint,
            same_value: Optional[Callable[[int], None]] = None,
            completed: Optional[Callable[[], None]] = None
    ):
        request_ = request.Request(bottom_left, top_right, same_value, completed)
        self._requests.append(request_)
        self._requested[bottom_left.y: top_right.y + 1, bottom_left.x: top_right.x + 1] = True

    def grid_lines_request(
            self,
            step: int
    ):
        self._requested[:, ::step] = True
        self._requested[::step, :] = True

    def request_incomplete(self):
        self._requested = ~self._completed

    def fill_box_request(
            self,
            bottom_left: tuples.PixelPoint,
            top_right: tuples.PixelPoint,
            value: int,
            completed: Optional[Callable[[], None]] = None
    ):
        # avoid device switching
        # self._box_iter_cpu[bottom_left.y: top_right.y + 1, bottom_left.x: top_right.x + 1] = 10
        self._box_iter_cpu[bottom_left.y: top_right.y + 1, bottom_left.x: top_right.x + 1] = value
        self._box_fill_cpu[bottom_left.y: top_right.y + 1, bottom_left.x: top_right.x + 1] = True
        self._box_fills = True
        if completed is not None:
            completed()

    def serve(self, early_stopping: bool = False) -> Generator[float, None, None]:
        if self._box_fills:
            self._do_box_fills()
        yield from self._compute_new_requests(early_stopping)
        self._respond_to_requests()
        self._reset()

    def _do_box_fills(self):
        box_fill_gpu = cp.asarray(self._box_fill_cpu)
        box_iter_gpu = cp.asarray(self._box_iter_cpu)

        self._completed[box_fill_gpu] = True
        self._iteration[box_fill_gpu] = box_iter_gpu[box_fill_gpu]

    def _compute_new_requests(self, early_stopping: bool = False) -> Generator[float, None, None]:
        # find new requests (2D)
        new_requests = self._requested & ~self._completed  # ~ is logical_not
        request_count = cp.count_nonzero(new_requests)
        if request_count == 0:
            return
        # print(f"\n# requests = \t{request_count}")
        # create 1D array of new c values to compute
        to_compute_flat = self._c[new_requests]
        # get the result as a flat array
        result_flat = yield from self._compute_manager.compute_flat_array(
            to_compute_flat,
            # early_stopping,
            self._early_stopping_iteration
        )
        # early_stop_iteration = self._compute_manager.early_stop_iteration
        # if self._mandel.early_stop_iteration <= self._compute_manager.early_stop_iteration:
        #     self._mandel.early_stop_iteration = self._compute_manager.early_stop_iteration

        # print(f"result_flat_max = {cp.amax(result_flat)}")
        # mark all the new_requests as completed (so don't compute again)
        self._completed[new_requests] = True
        # populate 2D iteration array with the results
        self._iteration[new_requests] = result_flat

    def _respond_to_requests(self):
        for request_ in self._requests:
            request_.respond(self._iteration)

    def _reset(self):
        self._requested.fill(False)
        self._requests.clear()
        self._box_iter_cpu.fill(0)
        self._box_fill_cpu.fill(False)

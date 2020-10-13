from __future__ import annotations

from typing import Optional, Callable, List, Generator, Union

import numpy as np
# import cupy as cp
try:
    import cupy as cp
except ImportError:
    cp = None
except AttributeError:
    cp = None

from mandel_app import tuples

from mandel_app.model.mandelbrot import mandel, compute
from mandel_app.model.mandelbrot.server import request, pixels

if cp is None:
    xp_ndarray = np.ndarray
else:
    xp_ndarray = Union[np.ndarray, cp.ndarray]


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
        self.pixels: pixels.Pixels = pixels.Pixels(shape=shape, has_cuda=self._compute_manager.has_cuda)

        # self._iteration: xp_ndarray
        # self._completed: xp_ndarray
        # self._requested: xp_ndarray
        # self._c: xp_ndarray
        # if self._compute_manager.has_cuda:
        #     self._iteration = cp.zeros(shape=shape, dtype=cp.int32)
        #     self._completed = cp.zeros(shape=shape, dtype=cp.bool)
        #     self._requested = cp.zeros(shape=shape, dtype=cp.bool)
        #     self._c = cp.zeros(shape=shape, dtype=cp.float64)
        # else:
        #     self._iteration = np.zeros(shape=shape, dtype=np.int32)
        #     self._completed = np.zeros(shape=shape, dtype=np.bool)
        #     self._requested = np.zeros(shape=shape, dtype=np.bool)
        #     self._c = np.zeros(shape=shape, dtype=np.float64)

        self._requests: List[request.Request] = []

        self._box_fills: bool = False
        # self._box_iter_cpu: np.ndarray = np.zeros(shape=shape, dtype=np.int32)
        # self._box_fill_cpu: np.ndarray = np.zeros(shape=shape, dtype=np.bool)

        self._build()

    def _build(self):
        self._initialize_c_and_z()

        if self._prev_mandel is not None and self._offset is not None:
            self._copy_over_prev()

    def _initialize_c_and_z(self):
        """Found to be faster using numpy, ogrid presumably not possible to parallelize."""
        m = self._new_mandel
        y, x = np.ogrid[-m.y_size/2.0: m.y_size/2.0: m.shape.y * 1j,
                        -m.x_size/2.0: m.x_size/2.0: m.shape.x * 1j]
        complex_grid: np.ndarray = m.centre + x*m.x_unit + y*m.y_unit

        if self._compute_manager.has_cuda:
            if m.mandel_julia == "mandel":
                self.pixels.c = cp.asarray(complex_grid)
                self.pixels.z = cp.copy(self.pixels.c)
        else:
            if m.mandel_julia == "mandel":
                self.pixels.c = complex_grid
                self.pixels.z = np.copy(self.pixels.c)

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

            if self._compute_manager.has_cuda:
                prev_iteration = cp.asarray(self._prev_mandel.iteration)
            else:
                prev_iteration = self._prev_mandel.iteration

            self.pixels.iteration[new_slice_y, new_slice_x] = prev_iteration[prev_slice_y, prev_slice_x]
            self.pixels.completed[new_slice_y, new_slice_x] = True
    # endregion

    @property
    def shape(self) -> tuples.ImageShape:
        return self._new_mandel.shape

    # TODO: implement for flatten
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
        self.pixels.requested[bottom_left.y: top_right.y + 1, bottom_left.x: top_right.x + 1] = True

    def grid_lines_request(
            self,
            step: int
    ):
        self.pixels.requested[:, ::step] = True
        self.pixels.requested[::step, :] = True

    def request_incomplete(self):
        self.pixels.requested = ~self.pixels.completed

    def fill_box_request(
            self,
            bottom_left: tuples.PixelPoint,
            top_right: tuples.PixelPoint,
            value: int,
            completed: Optional[Callable[[], None]] = None
    ):
        # avoid device switching
        # self._box_iter_cpu[bottom_left.y: top_right.y + 1, bottom_left.x: top_right.x + 1] = 10
        self.pixels.box_iter_cpu[bottom_left.y: top_right.y + 1, bottom_left.x: top_right.x + 1] = value
        self.pixels.box_fill_cpu[bottom_left.y: top_right.y + 1, bottom_left.x: top_right.x + 1] = True
        self._box_fills = True
        if completed is not None:
            completed()

    def serve(self) -> Generator[float, None, None]:
        if self._box_fills:
            self._do_box_fills()
        yield from self._compute_new_requests()
        self._respond_to_requests()
        self._reset()

    def _do_box_fills(self):
        if self._compute_manager.has_cuda:
            box_fill_gpu = cp.asarray(self.pixels.box_fill_cpu)
            box_iter_gpu = cp.asarray(self.pixels.box_iter_cpu)

            self.pixels.completed[box_fill_gpu] = True
            self.pixels.iteration[box_fill_gpu] = box_iter_gpu[box_fill_gpu]
        else:
            self.pixels.completed[self.pixels.box_fill_cpu] = True
            self.pixels.iteration[self.pixels.box_fill_cpu] = self.pixels.box_iter_cpu[self.pixels.box_fill_cpu]

    def _compute_new_requests(self) -> Generator[float, None, None]:
        # find new requests (2D)
        self.pixels.update_new_requests()
        if not self.pixels.has_new_requests:
            return
        # use 1D arrays of new values to compute
        result_flat = yield from self._compute_manager.compute_flat_array(
            self.pixels.new_requests_c,
            self.pixels.new_requests_z,
            self._early_stopping_iteration
        )
        # early_stop_iteration = self._compute_manager.early_stop_iteration
        # if self._mandel.early_stop_iteration <= self._compute_manager.early_stop_iteration:
        #     self._mandel.early_stop_iteration = self._compute_manager.early_stop_iteration

        # print(f"result_flat_max = {cp.amax(result_flat)}")
        # mark all the new_requests as completed (so don't compute again)
        self.pixels.completed[self.pixels.new_requests] = True
        # populate 2D iteration array with the results
        self.pixels.iteration[self.pixels.new_requests] = result_flat

    def _respond_to_requests(self):
        for request_ in self._requests:
            request_.respond(self.pixels.iteration)

    def _reset(self):
        self.pixels.requested.fill(False)
        self._requests.clear()
        self.pixels.box_iter_cpu.fill(0)
        self.pixels.box_fill_cpu.fill(False)
        self._box_fills = False

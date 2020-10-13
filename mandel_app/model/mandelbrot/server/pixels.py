from __future__ import annotations

from typing import Union

import numpy as np
try:
    import cupy as cp
except ImportError:
    cp = None
except AttributeError:
    cp = None

if cp is None:
    xp_ndarray = np.ndarray
else:
    # TODO: should this be xp_ndarray = cp.ndarray
    xp_ndarray = Union[np.ndarray, cp.ndarray]


# ideally we would have an object per pixel
# but for efficiently we need to use numpy/cupy array
# so do all the pixel operations here
# pixels could be points of z values or c values or both depending on what is being calculated
class Pixels:

    # region Setup
    def __init__(self,
                 shape: tuple,
                 has_cuda: bool
                 ):
        self.shape: tuple = shape
        self._has_cuda: bool = has_cuda

        self.iteration: xp_ndarray
        self.completed: xp_ndarray
        self.requested: xp_ndarray
        self.c: xp_ndarray
        if has_cuda:
            self.iteration = cp.zeros(shape=shape, dtype=cp.int32)
            self.completed = cp.zeros(shape=shape, dtype=cp.bool)
            self.requested = cp.zeros(shape=shape, dtype=cp.bool)
            self.new_requests = cp.zeros(shape=shape, dtype=cp.bool)
            self.c = cp.zeros(shape=shape, dtype=cp.float64)
        else:
            self.iteration = np.zeros(shape=shape, dtype=np.int32)
            self.completed = np.zeros(shape=shape, dtype=np.bool)
            self.requested = np.zeros(shape=shape, dtype=np.bool)
            self.new_requests = np.zeros(shape=shape, dtype=np.bool)
            self.c = np.zeros(shape=shape, dtype=np.float64)

        self.box_iter_cpu: np.ndarray = np.zeros(shape=shape, dtype=np.int32)
        self.box_fill_cpu: np.ndarray = np.zeros(shape=shape, dtype=np.bool)
    # endregion

    # region general properties
    @property
    def iteration_cpu(self) -> np.ndarray:
        if self._has_cuda:
            return cp.asnumpy(self.iteration)
        else:
            return self.iteration

    @property
    def c_cpu(self) -> np.ndarray:
        if self._has_cuda:
            return cp.asnumpy(self.c)
        else:
            return self.c

    @property
    def complete(self) -> bool:
        return self.completed.all()

    @property
    def incomplete_count(self) -> int:
        if self._has_cuda:
            return int(cp.count_nonzero(~self.completed))
        else:
            return int(np.count_nonzero(~self.completed))
    # endregion

    # region new requests
    def update_new_requests(self):
        self.new_requests = self.requested & ~self.completed

    @property
    def has_new_requests(self) -> bool:
        if self._has_cuda:
            # TODO: Test if this works: should do
            return bool(cp.any(self.new_requests))
            # return int(cp.count_nonzero(self.new_requests))
        else:
            return np.any(self.new_requests)

    # @property
    # def new_request_count(self) -> int:
    #     if self._has_cuda:
    #         return int(cp.count_nonzero(self.new_requests))
    #     else:
    #         return int(np.count_nonzero(self.new_requests))

    @property
    def new_requests_c(self) -> np.ndarray:
        return self.c[self.new_requests]
    # endregion

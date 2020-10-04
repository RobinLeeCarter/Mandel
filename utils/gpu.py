from typing import Optional

import cupy as cp


class Gpu:
    def __init__(self):
        self._has_cuda: Optional[bool] = None
        self._devices: Optional[int] = None

        try:
            self._devices = cp.cuda.runtime.getDeviceCount()
        except cp.cuda.runtime.CUDARuntimeError:
            self._devices = 0

        self._has_cuda = self._devices > 0

    @property
    def stream_ready(self) -> bool:
        if self._has_cuda:
            return cp.cuda.get_current_stream().done
        else:
            return False

    @property
    def has_cuda(self) -> bool:
        return self._has_cuda

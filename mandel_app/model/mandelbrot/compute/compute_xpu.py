from __future__ import annotations
import abc
from typing import Generator, Union

import numpy as np
# import cupy as cp
try:
    import cupy as cp
except ImportError:
    cp = None
except AttributeError:
    cp = None

if cp is None:
    xp_ndarray = np.ndarray
else:
    xp_ndarray = Union[np.ndarray, cp.ndarray]


# could be gpu or cpu but not both
class ComputeXpu(abc.ABC):
    def __init__(self):
        self.iterations_per_kernel: int = 0
        self._request_size: int = 0
        self._prev_total_iterations: int = 0

    # calculates iterations in parallel between start_iter and end_iter
    # inputs: a flat c gpu array and z starting values
    # outputs: z ending values and iterations (set to end_iter if still going)

    @abc.abstractmethod
    def compute_iterations(self,
                           c_in: xp_ndarray,
                           z_in: xp_ndarray,
                           iteration_in: xp_ndarray,
                           start_iter: int,
                           end_iter: int
                           ) -> Generator[float, None, None]:
        pass

    @abc.abstractmethod
    def _calculate_to(self, end_point: int) -> int:
        pass

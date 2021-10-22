from __future__ import annotations

import math
from typing import Generator, Optional, Union

import numpy as np
# import cupy as cp
try:
    import cupy as cp
except ImportError:
    cp = None
except AttributeError:
    cp = None

from mandel_app import application
from mandel_app.model.mandelbrot.compute import compute_xpu, compute_gpu, compute_cpu

if cp is None:
    xp_ndarray = np.ndarray
else:
    xp_ndarray = Union[np.ndarray, cp.ndarray]


# manager controls the calls to compute
# compute does the actual calculation
# Singleton
class ComputeManager:
    def __init__(self, max_iterations: int, early_stopping: bool = True):
        self.max_iterations: int = max_iterations
        self.early_stopping: bool = early_stopping
        self.final_iteration: int = 0
        self._compute: compute_xpu.ComputeXpu
        self._has_cuda = application.Application.instance().has_cuda
        if self._has_cuda:
            self._compute = compute_gpu.ComputeGpu()
        else:
            self._compute = compute_cpu.ComputeCpu()

    @property
    def has_cuda(self) -> bool:
        return self._has_cuda

    # input: a flat gpu array of c's to be calculated
    # output: a flat gpu array of the resulting iterations found
    # early_stopping: if no pixels have stopped in the latest loop then stop
    def compute_flat_array(
            self,
            new_requests_c: xp_ndarray,
            new_requests_z: xp_ndarray,
            early_stopping_iteration: Optional[int] = None
    ) -> Generator[float, None, xp_ndarray]:
        # print("compute_flat_array")
        # print(early_stopping_iteration)
        # print(self._has_cuda)

        if self._has_cuda:
            xp = cp
            self._compute.iterations_per_kernel = 1000
            kernels_per_loop = 10
            early_stop_tolerance: float = 0.0001
        else:
            xp = np
            self._compute.iterations_per_kernel = 1000
            kernels_per_loop = 1
            early_stop_tolerance: float = 0.0001
        iterations_per_loop = self._compute.iterations_per_kernel * kernels_per_loop
        total_pixels = new_requests_c.size
        pixel_tolerance = math.floor(early_stop_tolerance * total_pixels)

        # output array
        iteration_output: xp.ndarray = xp.zeros(shape=new_requests_c.shape, dtype=xp.int32)

        # initialise temporary loop arrays
        # initially every cell is continuing to be calculated
        continuing: xp.ndarray = xp.ones(shape=new_requests_c.shape, dtype=xp.bool)
        c: xp.ndarray = xp.copy(new_requests_c)
        z: xp.ndarray = xp.copy(new_requests_z)
        iteration: xp.ndarray = xp.copy(iteration_output)
        # start_iter: int = 0
        end_iter: int = 0

        while True:
            start_iter = end_iter
            end_iter = min(start_iter + iterations_per_loop, self.max_iterations)
            # print(f"{start_iter}->{end_iter}")
            count_continuing = xp.count_nonzero(continuing)
            # print(f"count_continuing:\t{count_continuing}")

            yield from self._compute.compute_iterations(c, z, iteration, start_iter, end_iter)

            # print(f"iteration.shape:\t{iteration.shape}")
            # noinspection PyTypeChecker
            still_continuing: xp.ndarray = (iteration == end_iter)
            count_still_continuing: int = xp.count_nonzero(still_continuing)
            trapped: xp.ndarray = (iteration == -1)

            count_stopped: int = xp.count_nonzero(xp.invert(still_continuing))
            count_trapped: int = xp.count_nonzero(trapped)
            count_escaped: int = count_stopped - count_trapped
            # print(f"count_still_continuing:\t{count_still_continuing}")
            # print(f"count_stopped:\t{count_stopped}")
            # print(f"count_trapped:\t{count_trapped}")
            # print(f"count_escaped:\t{count_escaped}")
            # print(f"continuing non-zero:\t{xp.count_nonzero(continuing)}")

            # print(f"iteration_output.shape:\t{iteration_output.shape}")
            # print(f"continuing.shape:\t{continuing.shape}")
            # print(f"iteration.shape:\t{iteration.shape}")
            # print(f"iteration_output.dtype:\t{iteration_output.dtype}")
            # print(f"continuing.dtype:\t{continuing.dtype}")
            # print(f"iteration.dtype:\t{iteration.dtype}")

            # good time to stop if no more were eliminated, assume the rest run to max_iterations
            # added check that this isn't because all pixels are continuing as this indicates
            # looking at a region where required iterations are high everywhere
            iteration_output[continuing] = iteration

            if count_still_continuing == 0 or end_iter == self.max_iterations:
                # if count_still_continuing == 0:
                #     print("0 continuing")
                # else:
                #     print("max iterations")
                break

            if self.early_stopping:
                if ((early_stopping_iteration is not None and
                     end_iter >= early_stopping_iteration)
                        or (early_stopping_iteration is None and
                            count_escaped <= pixel_tolerance and
                            count_still_continuing < total_pixels)):
                    # print("early_stopping")
                    continuing[continuing] = still_continuing
                    iteration_output[continuing] = self.max_iterations
                    break

            c = c[still_continuing]
            z = z[still_continuing]
            iteration = iteration[still_continuing]
            # print(f"xp.sum(continuing) before: {xp.sum(continuing)}")
            continuing[continuing] = still_continuing

        # trapped = (iteration == -1)
        # trapped_count = xp.count_nonzero(trapped)
        # print(f"trapped: {trapped_count}")

        iteration_output[iteration_output == -1] = self.max_iterations
        self.final_iteration = end_iter
        return iteration_output

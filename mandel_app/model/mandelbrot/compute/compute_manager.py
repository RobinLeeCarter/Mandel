from __future__ import annotations

import math
from typing import Generator, Optional, Union

import numpy as np
import cupy as cp

from mandel_app import application
from mandel_app.model.mandelbrot.compute import compute_xpu, compute_gpu, compute_cpu

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
            c: xp_ndarray,
            early_stopping_iteration: Optional[int] = None
    ) -> Generator[float, None, xp_ndarray]:
        xp = cp.get_array_module(c)
        z = xp.copy(c)
        # z = xp.zeros(shape=c.shape, dtype=xp.complex)
        iteration = xp.zeros(shape=c.shape, dtype=xp.int32)
        # early_stop = xp.zeros(shape=c.shape, dtype=xp.bool)

        # print(early_stopping_iteration)

        if self._has_cuda:
            self._compute.iterations_per_kernel = 1000
            kernels_per_loop = 10
            early_stop_tolerance: float = 0.0001
        else:
            self._compute.iterations_per_kernel = 1000
            kernels_per_loop = 1
            early_stop_tolerance: float = 0.0001
        iterations_per_loop = self._compute.iterations_per_kernel * kernels_per_loop

        total_pixels = c.size
        pixel_tolerance = math.floor(early_stop_tolerance * total_pixels)

        # first iteration different
        start_iter = 0
        end_iter = iterations_per_loop
        print(f"c.shape {c.shape}")
        print(f"{start_iter}->{end_iter}")
        print(f"iteration_max = {self.max_iterations}")
        # print(f"loop=0\t{start_iter}->{end_iter}")
        print(f"all:\t{c.size}")
        yield from self._compute.compute_iterations(c, z, iteration, start_iter, end_iter)

        continuing = (iteration == end_iter)
        if not xp.any(continuing):
            iteration[iteration == -1] = self.max_iterations
            self.final_iteration = end_iter
            return iteration

        continuing_c = c[continuing]
        continuing_z = z[continuing]
        continuing_iteration = iteration[continuing]

        # loop = 1
        # for multiplier in multipliers:
        while True:
            # for loop in range(1, loops):
            # start_iter = loop*iterations_per_loop
            # end_iter = min(start_iter + iterations_per_loop, self._max_iterations)
            start_iter = end_iter
            end_iter = min(start_iter + iterations_per_loop, self.max_iterations)
            print(f"{start_iter}->{end_iter}")
            count_continuing = xp.count_nonzero(continuing)
            print(f"count_continuing:\t{count_continuing}")

            # print(f"continuing_c.shape: {continuing_c.shape}")
            # print(f"continuing_z.shape: {continuing_z.shape}")
            # print(f"continuing_iteration.shape: {continuing_iteration.shape}")
            # print(f"continuing_c[0]: {continuing_c[100]}")
            # print(f"continuing_z[0]: {continuing_z[100]}")
            # next_z = continuing_z[100] * continuing_z[100] + continuing_c[100]
            # print(f"next z: {next_z}")
            # print(f"continuing_iteration[0]: {continuing_iteration[0]}")

            yield from self._compute.compute_iterations(
                continuing_c,
                continuing_z,
                continuing_iteration,
                start_iter,
                end_iter
            )

            # print(f"continuing_c[0]: {continuing_c[100]}")
            # print(f"continuing_z[0]: {continuing_z[100]}")
            # next_z = continuing_z[100] * continuing_z[100] + continuing_c[100]
            # print(f"next z: {next_z}")
            # print(f"continuing_iteration[0]: {continuing_iteration[0]}")

            # print(f"xp.sum(continuing) after compute: {xp.sum(continuing)}")
            # print(f"z.shape: {z.shape}")
            # print(f"continuing.shape: {continuing.shape}")

            # update main values
            z[continuing] = continuing_z   # may not need this but almost instant
            # noinspection PyTypeChecker
            still_continuing: xp.ndarray = (continuing_iteration == end_iter)
            count_still_continuing: int = xp.count_nonzero(still_continuing)
            count_stopped: int = xp.count_nonzero(xp.invert(still_continuing))
            print(f"count_still_continuing:\t{count_still_continuing}")
            print(f"count_stopped:\t{count_stopped}")

            # print(f"loop={loop} has {xp.count_nonzero(still_continuing)} pixels continuing")

            # good time to stop if no more were eliminated, assume the rest run to max_iterations
            # added check that this isn't because all pixels are continuing as this indicates high base iteration space
            iteration[continuing] = continuing_iteration
            if count_still_continuing == 0 or end_iter == self.max_iterations:
                if count_still_continuing == 0:
                    print("0 continuing")
                else:
                    print("max iterations")
                break

            if self.early_stopping:
                if ((early_stopping_iteration is not None and
                     end_iter >= early_stopping_iteration)
                        or (early_stopping_iteration is None and
                            count_stopped <= pixel_tolerance and
                            count_still_continuing < total_pixels)):
                    print("early_stopping")
                    continuing[continuing] = still_continuing
                    iteration[continuing] = self.max_iterations
                    break

            continuing_c = continuing_c[still_continuing]
            continuing_z = continuing_z[still_continuing]
            continuing_iteration = continuing_iteration[still_continuing]
            # print(f"xp.sum(continuing) before: {xp.sum(continuing)}")
            continuing[continuing] = still_continuing
            # loop += 1

        trapped = (iteration == -1)
        trapped_count = xp.count_nonzero(trapped)
        print(f"trapped: {trapped_count}")
        iteration[iteration == -1] = self.max_iterations

        # yield 1.0
        self.final_iteration = end_iter
        return iteration

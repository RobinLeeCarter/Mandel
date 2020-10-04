from __future__ import annotations
from typing import Generator
import multiprocessing
import itertools

import numpy as np

from mandel_app.model.mandelbrot.compute import compute_xpu, cpu_pixel


# all cpu
class ComputeCpu(compute_xpu.ComputeXpu):
    def __init__(self):  # high_precision=True)
        super().__init__()

        self._c: np.ndarray = np.array([], dtype=np.complex)
        self._z: np.ndarray = np.array([], dtype=np.complex)
        self._iteration: np.ndarray = np.array([], dtype=np.int32)

    # calculates iterations in parallel between start_iter and end_iter
    # inputs: a flat c gpu array and z starting values
    # outputs: z ending values and iterations (set to end_iter if still going)
    def compute_iterations(self,
                           c_in: np.ndarray,
                           z_in: np.ndarray,
                           iteration_in: np.ndarray,
                           start_iter: int,
                           end_iter: int
                           ) -> Generator[float, None, None]:
        # print(z_in[100])
        self._c = c_in
        self._z = z_in
        self._iteration = iteration_in
        self._request_size = iteration_in.size

        self._prev_total_iterations = np.sum(self._iteration)

        end_points = range(start_iter+self.iterations_per_kernel,
                           end_iter+1,
                           self.iterations_per_kernel)
        for end_point in end_points:
            # print(f"end_point: {end_point}")
            iterations_done = self._calculate_to(end_point)
            # print(f"iterations_done: {iterations_done}")
            yield float(iterations_done)
        # print(self._z[100])

        # z_in[:] = self._z[:]
        # iteration_in[:] = self._iteration[:]

        np.copyto(dst=z_in, src=self._z)
        np.copyto(dst=iteration_in, src=self._iteration)

    def _calculate_to(self, end_point: int) -> int:
        # print(self._z[100])

        with multiprocessing.Pool() as pool:
            results = pool.starmap(cpu_pixel.do_pixel,
                                   zip(self._c,
                                       self._z,
                                       self._iteration,
                                       itertools.repeat(end_point)
                                       )
                                   )
        self._z = np.array([z for z, i in results], dtype=np.complex)
        self._iteration = np.array([i for z, i in results], dtype=np.int32)

        # print(self._z[100])

        # approximation to the work done
        # return self._request_size * self.iterations_per_kernel
        # full calculation code:
        new_total_iterations = np.sum(self._iteration)
        iterations_done = new_total_iterations - self._prev_total_iterations
        self._prev_total_iterations = new_total_iterations
        return iterations_done

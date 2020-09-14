from __future__ import annotations

import math
from typing import Generator

import cupy as cp


# all gpu
class Compute:
    def __init__(self):  # high_precision=True)
        self._mandel_kernel: cp.RawKernel = self._load_mandel_kernel()

        self.iterations_per_kernel: int = 0

        # cupy mandel variables
        # experimentally this gives the best results
        # self.block_size: int = 32
        # according to cuda occupancy calculator this should give 100% occupancy vs 50% above
        self._BLOCK_SIZE: int = 64

        self._request_size: int = 0
        self._total_blocks: int = 0
        self._correct_size: int = 0

        self._c: cp.ndarray = cp.array([], dtype=cp.complex)
        self._z: cp.ndarray = cp.array([], dtype=cp.complex)
        self._iteration: cp.ndarray = cp.array([], dtype=cp.int32)

        self._prev_total_iterations: int = 0

    def _load_mandel_kernel(self) -> cp.RawKernel:
        file_name = r"mandel_app/model/mandelbrot/compute/compute_pixel.cu"
        with open(file_name, "r") as file:
            code = file.read()
        return cp.RawKernel(code, 'mandel_pixel')

    # calculates iterations in parallel between start_iter and end_iter
    # inputs: a flat c gpu array and z starting values
    # outputs: z ending values and iterations (set to end_iter if still going)

    # 32-threads is a Warp which is the minimum unit of execution
    # A Warp will be blocked by any threads that run to the end, so we do a chunk of iterations at a time
    # 48 SMs can each have at most 1024 concurrent threads = 32 active warps
    # each SM has 4 warp scheduler units - effect unknown
    # each SM provides 64 FP32 cores, 64 INT32 cores, 8 mixed-precision, 2 FP64 cores
    # each can also have a maximum of 16 blocks
    # so optimal block_size should be 64 threads (2 warps) as this would be 16 blocks each of 2 warps

    # my calculations: 6,624 total cores, 49,152 threads
    # so minimum number of pixels to calculate is somewhere between 10,000 and 50,000 perhaps
    # every tenth pixel would be 15,000

    # however optimal block size appears to be 32 threads (1 warp) even though this implies 50% occupancy

    # total maximum threads = 1024 *

    def compute_iterations(self,
                           c_in: cp.ndarray,
                           z_in: cp.ndarray,
                           iteration_in: cp.ndarray,
                           start_iter: int,
                           end_iter: int
                           ) -> Generator[float, None, None]:
        self._request_size = c_in.size
        # print(f"request_size = {request_size}")
        self._total_blocks = math.ceil(self._request_size / self._BLOCK_SIZE)
        # print(f"total_blocks = {total_blocks}")
        self._correct_size = self._total_blocks * self._BLOCK_SIZE
        # print(f"correct_size = {correct_size}")

        self._c = cp.empty(shape=(self._correct_size,), dtype=cp.complex)
        self._z = cp.empty(shape=(self._correct_size,), dtype=cp.complex)
        self._iteration = cp.empty(shape=(self._correct_size,), dtype=cp.int32)

        # no slower with the copy and copy back (presume very fast on GPU memory)
        self._c[:self._request_size] = c_in[:]
        self._z[:self._request_size] = z_in[:]
        self._iteration[:self._request_size] = iteration_in[:]
        if self._request_size < self._correct_size:
            self._c[self._request_size:] = 1.0
            self._z[self._request_size:] = 1.0
            self._iteration[self._request_size:] = 0
        self._prev_total_iterations = cp.sum(self._iteration[:self._request_size])

        # print(f"c.shape: {c.shape}")
        # print(f"cells: {cells}")
        # print(f"block_size: {self.block_size}")
        # print(f"total_blocks: {total_blocks}")

        end_points = range(start_iter+self.iterations_per_kernel,
                           end_iter+1,
                           self.iterations_per_kernel)
        for end_point in end_points:
            iterations_done = self.calculate_to(end_point)
            yield float(iterations_done)

        # end = cp.int32(end_iter)
        # print(end)
        # iterations_done = self.calculate_to(end_iter)
        # yield float(iterations_done)

        z_in[:] = self._z[:self._request_size]
        iteration_in[:] = self._iteration[:self._request_size]

    def calculate_to(self, end_point: int) -> int:
        end = cp.int32(end_point)
        self._mandel_kernel((self._total_blocks,), (self._BLOCK_SIZE,), (self._c, self._z, self._iteration, end))
        # approximation to the work done
        return self._request_size * self.iterations_per_kernel
        # full calculation code:
        # new_total_iterations = cp.sum(self._iteration[:self._request_size])
        # iterations_done = new_total_iterations - self._prev_total_iterations
        # self._prev_total_iterations = new_total_iterations
        # return iterations_done

from __future__ import annotations

import math
from typing import Optional

import cupy as cp


# all gpu
class Compute:
    def __init__(self):  # high_precision=True)
        self._mandel_kernel: cp.RawKernel = self._load_mandel_kernel()
        # cupy mandel variables
        self.block_size: int = 32

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
                           ):
        request_size = c_in.size
        # print(f"request_size = {request_size}")
        total_blocks = math.ceil(request_size/self.block_size)
        # print(f"total_blocks = {total_blocks}")
        correct_size = total_blocks * self.block_size
        # print(f"correct_size = {correct_size}")

        c = cp.empty(shape=(correct_size,), dtype=cp.complex)
        z = cp.empty(shape=(correct_size,), dtype=cp.complex)
        iteration = cp.empty(shape=(correct_size,), dtype=cp.int32)
        start = cp.int32(start_iter)
        end = cp.int32(end_iter)

        # no slower with the copy and copy back (presume very fast on GPU memory)
        c[:request_size] = c_in[:]
        z[:request_size] = z_in[:]
        iteration[:request_size] = iteration_in[:]

        # print(f"c.shape: {c.shape}")
        # print(f"cells: {cells}")
        # print(f"block_size: {self.block_size}")
        # print(f"total_blocks: {total_blocks}")

        self._mandel_kernel((total_blocks,), (self.block_size,), (c, z, iteration, start, end))
        z_in[:] = z[:request_size]
        iteration_in[:] = iteration[:request_size]

        # self._mandel_kernel((total_blocks,), (self.block_size,), (c_in, z_in, iteration_in, start, end))

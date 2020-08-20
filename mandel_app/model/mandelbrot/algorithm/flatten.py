from __future__ import annotations

import numpy as np
import cupy as cp

import utils

from mandel_app.model.mandelbrot.server import server


class Flatten:

    def __init__(self, server_: server.Server):
        self.server: server.Server = server_
        self._cpu_c = cp.asnumpy(self.server._c)
        self._timer: utils.Timer = utils.Timer()

    # simplest algorithm: just flatten the array, move it to the gpu and process all of it
    # takes in a 2D np array and computes it all in one go
    # output: 2D np array of iterations
    def run(self) -> np.ndarray:
        cpu_c_flat = self._cpu_c.flatten()  # 0.004s
        cpu_iteration_flat = self._calc_array(cpu_c_flat)
        # gpu_c_flat = cp.asarray(cpu_c_flat)
        # gpu_iteration_flat = compute_array.Compute.compute(gpu_c_flat)
        # cpu_iteration_flat = cp.asnumpy(gpu_iteration_flat)
        cpu_iteration = cpu_iteration_flat.reshape(self._cpu_c.shape)  # 0s time
        return cpu_iteration

    def speed_test(self) -> np.ndarray:
        self._timer.start()
        cpu_c_flat = self._cpu_c.flatten()  # 0.004s
        self._timer.lap("flatten")
        cpu_iteration_flat = self._calc_array(cpu_c_flat)
        # cpu_iteration = cpu_iteration_flat.reshape(self._cpu_c.shape)
        self._timer.lap(f"full\t{cpu_c_flat.size}")
        # block_size = int(cpu_c_flat.shape[0] / 100)
        for i in range(1, 21):
            size = 2 ** i
            cpu_flat = cpu_c_flat[0:size]
            # self._timer.lap(f"prep {size}")
            cpu_iteration_flat = self._calc_array(cpu_flat)
            # cpu_iteration = cpu_iteration_flat.reshape(self._cpu_c.shape)
            time = self._timer.lap(f"calc\t{size}")
            mega_pixels_per_second = (size / time) / 10**6
            print(f"{size} pixels\t{mega_pixels_per_second:.4f} mega-pixels/s")

        cpu_iteration_flat = self._calc_array(cpu_c_flat)
        self._timer.lap(f"full\t{cpu_c_flat.size}")
        cpu_iteration = cpu_iteration_flat.reshape(self._cpu_c.shape)
        # self._timer.lap("reshape")
        self._timer.stop()
        return cpu_iteration

    def _calc_array(self, cpu_c_flat: np.ndarray) -> np.ndarray:
        gpu_c_flat = cp.asarray(cpu_c_flat)
        gpu_iteration_flat = self.server._compute_flat_array(gpu_c_flat)
        cpu_iteration_flat = cp.asnumpy(gpu_iteration_flat)
        # cpu_iteration_flat = compute_array.Compute.compute(cpu_c_flat)
        return cpu_iteration_flat

from __future__ import annotations

import math
from typing import Generator, Optional

import cupy as cp

from mandel_app.model.mandelbrot.compute import compute


# manager controls the calls to compute
# compute does the actual calculation
# Singleton
class ComputeManager:
    def __init__(self, max_iterations: int, early_stopping: bool = True):
        self.max_iterations: int = max_iterations
        self.early_stopping: bool = early_stopping
        self._compute: compute.Compute = compute.Compute()
        self.final_iteration: int = 0

    # input: a flat gpu array of c's to be calculated
    # output: a flat gpu array of the resulting iterations found
    # early_stopping: if no pixels have stopped in the latest loop then stop
    def compute_flat_array(
            self,
            c: cp.ndarray,
            # early_stopping: bool = False,
            early_stopping_iteration: Optional[int] = None
    ) -> Generator[float, None, cp.ndarray]:
        z = cp.zeros(shape=c.shape, dtype=cp.complex)
        iteration = cp.zeros(shape=c.shape, dtype=cp.int32)
        # early_stop = cp.zeros(shape=c.shape, dtype=cp.bool)

        # print(early_stopping_iteration)

        # desired_loops: int = 5
        # multiplier_per_loop: float = 1.0

        # iterations_per_loop = 10000
        # early_stop_tolerance: float = 0.0001

        iterations_per_loop = 1000
        early_stop_tolerance: float = 0.00001

        total_pixels = c.size
        pixel_tolerance = math.floor(early_stop_tolerance * total_pixels)

        # multipliers = self.multipliers(multiplier_per_loop)  # generator
        # desired_multiplier = sum(multipliers.__next__() for _ in range(desired_loops))
        # initial_iterations = math.ceil(float(expected_iterations) / desired_multiplier)
        # multipliers = self.multipliers(multiplier_per_loop)  # reset generator
        # iterations_per_loop = 10000

        # loops = 100     # optimal with early_stopping
        # loops = 10      # optimal without early_stopping
        # starting_iterations = math.ceil(self._mandel.max_iterations * (2**-loops))
        # iterations_per_loop = math.ceil(self._max_iterations / loops)
        # yield_per_loop: float = 1.0 / float(loops+4)
        # yield_per_iteration: float = 1.0 / float(self._mandel.max_iterations + starting_iterations*4)

        # first iteration different
        start_iter = 0
        end_iter = iterations_per_loop
        # end_iter = starting_iterations
        # performed_iter = start_iter - end_iter
        # print(f"{c.shape}")
        # print(f"{start_iter}->{end_iter}")
        # print(f"iteration_max = {cp.amax(iteration)}")
        # print(f"loop=0\t{start_iter}->{end_iter}")
        # print(f"all:\t{c.size}")
        self._compute.compute_iterations(c, z, iteration, start_iter, end_iter)
        yield self.calc_work_done(iteration, start_iter)
        # claim 4-times the progress for the first one (usually much slower)
        # yield starting_iterations * 4 * yield_per_iteration
        # yield yield_per_loop * 4  # claim 4-times the progress for the first one (usually much slower)
        # print(f"iteration_max = {cp.amax(iteration)}")
        continuing = (iteration == end_iter)
        if not cp.any(continuing):
            return iteration

        continuing_c = c[continuing]
        continuing_z = z[continuing]
        continuing_iteration = iteration[continuing]

        loop = 1
        # for multiplier in multipliers:
        while True:
            # for loop in range(1, loops):
            # start_iter = loop*iterations_per_loop
            # end_iter = min(start_iter + iterations_per_loop, self._max_iterations)
            start_iter = end_iter
            end_iter = min(start_iter + iterations_per_loop, self.max_iterations)
            # performed_iter = start_iter - end_iter
            # print(f"loop={loop}\t{start_iter}->{end_iter}")
            # count_continuing = cp.count_nonzero(continuing)
            # print(f"cont:\t{count_continuing}")

            # print(f"continuing_c.shape: {continuing_c.shape}")
            # print(f"continuing_z.shape: {continuing_z.shape}")
            # print(f"continuing_iteration.shape: {continuing_iteration.shape}")
            self._compute.compute_iterations(
                continuing_c,
                continuing_z,
                continuing_iteration,
                start_iter,
                end_iter
            )
            yield self.calc_work_done(continuing_iteration, start_iter)
            # yield (starting_iterations * 3 + end_iter) * yield_per_iteration
            # yield yield_per_loop * (loop + 4)
            # print(f"cp.sum(continuing) after compute: {cp.sum(continuing)}")
            # print(f"z.shape: {z.shape}")
            # print(f"continuing.shape: {continuing.shape}")

            # update main values
            z[continuing] = continuing_z   # may not need this but almost instant
            # noinspection PyTypeChecker
            still_continuing: cp.ndarray = (continuing_iteration == end_iter)
            count_still_continuing: int = cp.count_nonzero(still_continuing)
            count_stopped: int = cp.count_nonzero(cp.invert(still_continuing))
            # print(f"still:\t{count_still_continuing}")
            # print(f"stop:\t{count_stopped}")

            # print(f"loop={loop} has {cp.count_nonzero(still_continuing)} pixels continuing")

            # good time to stop if no more were eliminated, assume the rest run to max_iterations
            # added check that this isn't because all pixels are continuing as this indicates high base iteration space
            iteration[continuing] = continuing_iteration
            if count_still_continuing == 0 or end_iter == self.max_iterations:
                break

            if self.early_stopping:
                # print(early_stopping_iteration)
                if ((early_stopping_iteration is not None and
                     end_iter >= early_stopping_iteration)
                        or (early_stopping_iteration is None and
                            count_stopped <= pixel_tolerance and
                            count_still_continuing < total_pixels)):
                    continuing[continuing] = still_continuing
                    iteration[continuing] = self.max_iterations
                    break

            continuing_c = continuing_c[still_continuing]
            continuing_z = continuing_z[still_continuing]
            continuing_iteration = continuing_iteration[still_continuing]
            # print(f"cp.sum(continuing) before: {cp.sum(continuing)}")
            continuing[continuing] = still_continuing
            loop += 1

        # yield 1.0
        self.final_iteration = end_iter
        return iteration

    def calc_work_done(self, iteration: cp.ndarray, start_iter: int) -> float:
        total_iterations = cp.sum(iteration)
        base_iterations = start_iter * iteration.size
        extra_iterations = total_iterations - base_iterations
        # print(f"total_iterations={total_iterations}")
        # print(f"base_iterations={base_iterations}")

        return float(extra_iterations)

    # @staticmethod
    # def multipliers(factor: float = 2.0):
    #     i: float = 1.0
    #     while True:
    #         yield i
    #         i *= factor

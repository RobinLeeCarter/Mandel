from __future__ import annotations

import copy
from typing import Generator, Optional

# import utils
import thread
from mandel_app import tuples
from mandel_app.model.mandelbrot import mandel, algorithm, server, compute, mandel_progress_estimator


class MandelJob(thread.Job):
    def __init__(self,
                 compute_manager: compute.ComputeManager,
                 new_mandel: mandel.Mandel,
                 prev_mandel: Optional[mandel.Mandel] = None,
                 offset: Optional[tuples.PixelPoint] = None,
                 display_progress: bool = True,
                 save_history: bool = False):
        super().__init__()
        self._compute_manager: compute.ComputeManager = compute_manager
        self._new_mandel: mandel.Mandel = copy.deepcopy(new_mandel)
        self._prev_mandel: Optional[mandel.Mandel] = prev_mandel
        # offset vector from prev_mandel origin to new_mandel origin (this already includes any pan)
        self._offset: Optional[tuples.PixelPoint] = offset
        if display_progress:
            self.progress_estimator = mandel_progress_estimator.MandelProgressEstimator()
        self.save_history: bool = save_history

    def set_previous_mandel(self,
                            prev_mandel: mandel.Mandel,
                            offset: tuples.PixelPoint
                            ):
        self._prev_mandel = prev_mandel
        self._offset = offset

    @property
    def new_mandel(self) -> mandel.Mandel:
        return self._new_mandel

    # calculates a mandel using whatever algorithm is implemented
    def _exec(self) -> Generator[float, None, None]:
        pixel_count: int = 0    # just to make warning go away

        # set up arrays and do any copy-over from previous results that's possible
        yield 0.0
        if self.progress_estimator:
            self.progress_estimator.set_progress_range(0.05)

        # if adding a border want to use the same early_stopping_iteration
        if self._new_mandel.has_border and self._new_mandel.final_iteration > 0:
            early_stopping_iteration = self._new_mandel.final_iteration
        else:
            early_stopping_iteration = None
        # create a server for the algorithm and start it based on self._mandel
        server_ = server.Server(
            self._compute_manager,
            self._new_mandel,
            early_stopping_iteration,
            self._prev_mandel,
            self._offset
        )
        yield 1.0

        # find expected work after any copy-over (e.g. from panning)
        if self.progress_estimator:
            pixel_count = server_.incomplete_count
            # pixel_count = self.get_pixel_count(self._new_mandel)  # , self._pan)
            expected_work = pixel_count * self._new_mandel.expected_iterations_per_pixel
            # print(f"pixel_count: {pixel_count}")
            print(f"expected_it_per_pixel:\t{self._new_mandel.expected_iterations_per_pixel}")
            print(f"expected_iterations:\t{expected_work}")
            self.progress_estimator.set_expected_work(expected_work)

        # run the algorithm

        # for i in range(10):
        #     algorithm_ = algorithm.Flatten(server_)
        #     self._mandel.iteration = algorithm_.run()
        # self._mandel.iteration = algorithm_.speed_test()

        # algorithm_ = algorithm.RequestAll(compute_server_, m.shape)
        # self._mandel.iteration = algorithm_.run()

        # algorithm_ = algorithm.BoxAlgorithm(compute_server_, m.shape)
        # self._mandel.iteration = algorithm_.run()

        algorithm_ = algorithm.Mesh(server_, self.progress_estimator)

        self._new_mandel.iteration = yield from algorithm_.run()

        # self._new_mandel.iteration_shape = self._new_mandel.shape
        # self._new_mandel.iteration_offset = self._new_mandel.offset
        self._new_mandel.max_iteration = self._compute_manager.max_iterations

        # set mandel statistics
        if self.progress_estimator:
            self._new_mandel.iterations_performed = int(self.progress_estimator.cumulative_work)
            self._new_mandel.iterations_per_pixel = float(self._new_mandel.iterations_performed) / float(pixel_count)
            print(f"iterations_performed:\t{self._new_mandel.iterations_performed}")
            print(f"iterations_per_pixel:\t{self._new_mandel.iterations_per_pixel}")

        # print("self._compute_manager.final_iteration=", self._compute_manager.final_iteration)
        if not self._new_mandel.has_border:
            self._new_mandel.final_iteration = self._compute_manager.final_iteration

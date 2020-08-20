from __future__ import annotations

from typing import Generator, Optional

# import utils
import thread
from mandel_app.model.mandelbrot import mandel, algorithm, server, compute, mandel_progress_estimator


class MandelJob(thread.Job):
    def __init__(self,
                 compute_manager: compute.ComputeManager,
                 mandel_: mandel.Mandel,
                 display_progress: bool = True,
                 save_history: bool = False,
                 **kwargs):
        super().__init__(data=mandel_, **kwargs)
        self._compute_manager: compute.ComputeManager = compute_manager
        assert isinstance(self._data[0], mandel.Mandel)
        self._mandel: mandel.Mandel = self._data[0]
        self.save_history: bool = save_history

        if display_progress:
            self.progress_estimator = mandel_progress_estimator.MandelProgressEstimator()

    # calculates a mandel using whatever algorithm is implemented
    def _exec(self) -> Generator[float, None, None]:
        pixel_count: int = 0    # just to make warning go away

        if self.progress_estimator:
            pixel_count = self.get_pixel_count(self._mandel)  # , self._pan)
            expected_work = pixel_count * self._mandel.expected_iterations_per_pixel
            self.progress_estimator.set_expected_work(expected_work)

        yield 0.0
        if self.progress_estimator:
            self.progress_estimator.set_progress_range(0.05)

        # if adding a border want to use the same early_stopping_iteration
        if self._mandel.has_border and self._mandel.final_iteration > 0:
            early_stopping_iteration = self._mandel.final_iteration
        else:
            early_stopping_iteration = None
        # create a server for the algorithm and start it based on self._mandel
        server_ = server.Server(self._mandel, self._compute_manager, early_stopping_iteration)

        yield 1.0

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

        self._mandel.iteration = yield from algorithm_.run()

        self._mandel.iteration_shape = self._mandel.shape
        self._mandel.iteration_offset = self._mandel.offset
        self._mandel.max_iteration = self._compute_manager.max_iterations

        # set mandel statistics
        if self.progress_estimator:
            self._mandel.iterations_performed = int(self.progress_estimator.cumulative_work)
            self._mandel.iterations_per_pixel = float(self._mandel.iterations_performed) / float(pixel_count)

        # print("self._compute_manager.final_iteration=", self._compute_manager.final_iteration)
        if not self._mandel.has_border:
            self._mandel.final_iteration = self._compute_manager.final_iteration

    def get_pixel_count(self,
                        mandel_: mandel.Mandel
                        # pan: Optional[tuples.PixelPoint]
                        ) -> int:
        pixel_count: int
        if mandel_.pan is None:
            pixel_count = mandel_.shape.x * mandel_.shape.y
        else:
            abs_x = abs(mandel_.pan.x)
            abs_y = abs(mandel_.pan.y)
            pixel_count = \
                abs_x * (mandel_.shape.y - abs_y) + \
                abs_y * (mandel_.shape.x - abs_x) + \
                abs_x * abs_y
        return pixel_count

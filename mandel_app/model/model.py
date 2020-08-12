from __future__ import annotations

import copy
from typing import Optional, List

from mandel_app import controller, tuples
import thread
from mandel_app.model import mandelbrot, z_model

MAX_ITERATIONS = 1000000


class Model:
    # region Setup
    def __init__(self):
        self._controller: Optional[controller.Controller] = None
        self._compute_manager: Optional[mandelbrot.ComputeManager] = None
        self._calc_thread_manager: Optional[thread.Manager] = None
        self.new_mandel: Optional[mandelbrot.Mandel] = None
        self.displayed_mandel: Optional[mandelbrot.Mandel] = None
        self.mandel_history: List[mandelbrot.Mandel] = []
        self.z_model: Optional[z_model.ZModel] = None

    def set_controller(self, controller_: controller.Controller):
        self._controller = controller_

    def build(self, image_space: tuples.ImageShape):
        self.new_mandel = self._initial_mandel(image_space)
        self._compute_manager = mandelbrot.ComputeManager(MAX_ITERATIONS)
        self._calc_thread_manager = thread.Manager(
            on_progress_update=self._on_progress_update,
            on_stop_success=self._on_stop_success,
            on_job_complete=self._on_job_complete
        )
        self.z_model = z_model.ZModel()
        # self.z_model.build(z0=complex(real=0.24091, imag=0.55),
        self.z_model.build(z0=self.new_mandel.centre,
                           image_shape=tuples.ImageShape(x=700, y=700))

        self._calc_thread_manager.start_thread()

    def _initial_mandel(self, image_space: tuples.ImageShape) -> mandelbrot.Mandel:
        mandel = mandelbrot.Mandel(centre=complex(-0.5, 0.0), size=2.4,
                                   shape=image_space,
                                   expected_iterations_per_pixel=1750
                                   )
        return mandel

    def _test_mandel(self, image_space: tuples.ImageShape) -> mandelbrot.Mandel:
        mandel = mandelbrot.Mandel(centre=complex(0.1, 0.1), size=0.2,
                                   shape=image_space
                                   )
        return mandel

    def _different_mandel(self, image_space: tuples.ImageShape) -> mandelbrot.Mandel:
        mandel = mandelbrot.Mandel(centre=complex(-0.745428, 0.113009), size=3.0E-5,
                                   shape=image_space
                                   )
        return mandel
    # endregion

    # region Controller Messages
    def start_test_mandel(self, image_space: tuples.ImageShape):
        self.new_mandel = self._test_mandel(image_space)

    def start_different_mandel(self, image_space: tuples.ImageShape):
        self.new_mandel = self._different_mandel(image_space)

    def calc_new_mandel(self, save_history: bool = False):
        job = mandelbrot.MandelJob(
            self._compute_manager,
            self.new_mandel,
            save_history=save_history
        )
        self._calc_thread_manager.request_job(job, queue_as=thread.QueueAs.SINGULAR)

    def new_is_displayed(self, save_history: bool = True):
        if save_history and self.displayed_mandel is not None:
            self.mandel_history.append(self.displayed_mandel)
        self.displayed_mandel = self.new_mandel
        self.new_mandel = copy.deepcopy(self.new_mandel)

    def revert_to_displayed_as_new(self):
        self.new_mandel = copy.deepcopy(self.displayed_mandel)

    def zoom_and_calc(self,
                      image_space: tuples.ImageShape,
                      pixel_point: Optional[tuples.PixelPoint],
                      scaling: float):
        if pixel_point is None:
            new_centre = self.displayed_mandel.centre
        else:
            new_centre = self.displayed_mandel.get_complex_from_pixel(pixel_point)

        save_history: bool = (scaling < 1)

        self.new_mandel = mandelbrot.Mandel(
            centre=new_centre,
            size_per_gap=self.displayed_mandel.size_per_gap * scaling,
            shape=image_space,
            theta_degrees=self.displayed_mandel.theta_degrees,
            expected_iterations_per_pixel=self.displayed_mandel.iterations_per_pixel
        )

        self.calc_new_mandel(save_history=save_history)

    def rotate_and_calc(self, theta: int):
        self.new_mandel.theta_degrees = theta
        if self.new_mandel.has_border:
            self.new_mandel.remove_border()
        self.calc_new_mandel()

    def pan_and_calc(self, pan: tuples.PixelPoint):
        self.new_mandel.pan = pan
        if self.new_mandel.has_border:
            self.new_mandel.remove_border()
        self.calc_new_mandel()

    def restore_previous_as_new(self):
        if self.mandel_history:
            self.new_mandel = self.mandel_history.pop()
        else:
            # reset new_mandel
            self.new_mandel = copy.deepcopy(self.displayed_mandel)
        self._controller.new_is_ready()

    def request_stop(self):
        self._calc_thread_manager.request_stop()

    def set_compute_parameters(self, max_iterations: Optional[int] = None, early_stopping: bool = True):
        if max_iterations is None:
            self._compute_manager.max_iterations = MAX_ITERATIONS
        else:
            self._compute_manager.max_iterations = max_iterations
        self._compute_manager.early_stopping = early_stopping
    # endregion

    # region Events from Thread
    def _on_progress_update(self, progress: float, job_number: int):
        self._controller.progress_update(progress)

    def _on_stop_success(self):
        self._controller.stop_success()

    def _on_job_complete(self, job: thread.Job):
        mandel = job.get_data()
        assert isinstance(mandel, mandelbrot.Mandel)
        assert isinstance(job, mandelbrot.MandelJob)
        self.new_mandel = mandel
        # print(f"completed job id = {id(job)}")
        if job.progress_estimator:  # only show time for borderless calculation
            self.new_mandel.time_taken = job.progress_estimator.timer.total
        self._controller.new_is_ready(job.save_history)

        # TODO: control generation of borders in controller rather than automatically firing?
        if not self.new_mandel.has_border:
            self._add_border()

    def _add_border(self):
        self.new_mandel.add_border(14*4*5, 14*4*5)
        job = mandelbrot.MandelJob(
            self._compute_manager,
            self.new_mandel,
            display_progress=False,  # background job
            save_history=False
        )
        self._calc_thread_manager.request_job(job, queue_as=thread.QueueAs.ENQUEUE)
    # endregion

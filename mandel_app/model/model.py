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
        # needed for creating new mandels to the correct size
        self._frame_shape: Optional[tuples.ImageShape] = None
        self.displayed_mandel: Optional[mandelbrot.Mandel] = None
        self.new_mandel: Optional[mandelbrot.Mandel] = None
        self.mandel_history: List[mandelbrot.Mandel] = []
        self.z_model: Optional[z_model.ZModel] = None

    def set_controller(self, controller_: controller.Controller):
        self._controller = controller_

    def build(self, frame_shape: tuples.ImageShape):
        self._frame_shape = frame_shape
        self.displayed_mandel = self._initial_mandel()
        # self.displayed_mandel = self._slow_mandel()
        # self.displayed_mandel = self._different_mandel()
        self.new_mandel = self.displayed_mandel.lite_copy()
        self._compute_manager = mandelbrot.ComputeManager(MAX_ITERATIONS)
        self._calc_thread_manager = thread.Manager(
            on_progress_update=self._on_progress_update,
            # on_active_change=self._on_active_change,
            on_stop_success=self._on_stop_success,
            on_job_complete=self._on_job_complete
        )
        self.z_model = z_model.ZModel()
        # self.z_model.build(z0=complex(real=0.24091, imag=0.55),
        self.z_model.build(z0=self.displayed_mandel.centre,
                           image_shape=tuples.ImageShape(x=700, y=700))

        self._calc_thread_manager.start_thread()

    # @property
    # def calc_thread_active(self) -> bool:
    #     return self._calc_thread_manager.state.worker_active

    @property
    def calc_thread_state(self) -> thread.State:
        return self._calc_thread_manager.state
    # endregion

    # region Controller Messages
    def on_resized(self, frame_shape: tuples.ImageShape):
        self._frame_shape = frame_shape
        self.pan_and_calc(pan=None)

    def calc_new_mandel(self, offset: Optional[tuples.PixelPoint] = None, save_history: bool = False):
        mandel_job = mandelbrot.MandelJob(
            compute_manager=self._compute_manager,
            new_mandel=self.new_mandel,
            save_history=save_history
        )
        if offset is not None:
            mandel_job.set_previous_mandel(prev_mandel=self.displayed_mandel, offset=offset)

        self._calc_thread_manager.request_job(mandel_job, queue_as=thread.QueueAs.SINGULAR)

    def new_is_displayed(self, save_history: bool = True):
        if save_history and self.displayed_mandel is not None:
            self.mandel_history.append(self.displayed_mandel)
        self.displayed_mandel = self.new_mandel
        # self.new_mandel = copy.deepcopy(self.new_mandel)

    # def revert_to_displayed_as_new(self):
    #     self.new_mandel = copy.deepcopy(self.displayed_mandel)

    def zoom_and_calc(self,
                      frame_point: Optional[tuples.PixelPoint],
                      scaling: float):
        if frame_point is None:
            new_centre = self.displayed_mandel.centre
        else:
            new_centre = self.displayed_mandel.get_complex_from_frame_point(
                self._frame_shape, frame_point)

        save_history: bool = (scaling < 1)

        self.new_mandel = self.displayed_mandel.lite_copy(
            centre=new_centre,
            size_per_gap=self.displayed_mandel.size_per_gap * scaling,
            shape=self._frame_shape,
            expected_iterations_per_pixel=self.displayed_mandel.iterations_per_pixel,
            has_border=False
        )

        # self.new_mandel = mandelbrot.Mandel(
        #     centre=new_centre,
        #     size_per_gap=self.displayed_mandel.size_per_gap * scaling,
        #     shape=self._frame_shape,
        #     theta_degrees=self.displayed_mandel.theta_degrees,
        #     expected_iterations_per_pixel=self.displayed_mandel.iterations_per_pixel
        # )

        self.calc_new_mandel(save_history=save_history)

    def rotate_and_calc(self, theta: int):
        self.new_mandel = self.displayed_mandel.lite_copy(
            theta_degrees=theta,
            shape=self._frame_shape,
            has_border=False
        )
        # self.new_mandel.theta_degrees = theta
        # self.new_mandel.has_border = False
        # self.new_mandel.shape = self._frame_shape
        # if self.new_mandel.has_border:
        #     self.new_mandel.remove_border()
        self.calc_new_mandel()

    def pan_and_calc(self, pan: Optional[tuples.PixelPoint] = None):

        self.new_mandel = self.displayed_mandel.lite_copy(
            shape=self._frame_shape,
            has_border=False
        )

        if pan is not None:
            # print(f"model.frame_shape: {self._frame_shape}")
            # new_centre_frame_point = tuples.PixelPoint(
            #     x=float(self._frame_shape.x) / 2.0 + pan.x,
            #     y=float(self._frame_shape.y) / 2.0 + pan.y
            # )
            # self.new_mandel.centre = self.displayed_mandel.get_complex_from_frame_point(
            #     self._frame_shape, new_centre_frame_point)

            self.new_mandel.centre = self.displayed_mandel.get_complex_from_center_diff(pan)

        # if pan is not None:
        #     new_centre_frame_point = tuples.PixelPoint(
        #         x=float(self._frame_shape.x) / 2.0 + pan.x,
        #         y=float(self._frame_shape.y) / 2.0 + pan.y
        #     )
        #     self.new_mandel.centre = self.new_mandel.get_complex_from_frame_point(new_centre_frame_point)

        offset = self._calc_offset(previous_shape=self.displayed_mandel.shape,
                                   new_shape=self.new_mandel.shape,
                                   pan=pan)
        self.calc_new_mandel(offset=offset)

        # self.new_mandel.has_border = False
        # self.new_mandel.shape = self._frame_shape
        # self.new_mandel.pan = pan
        # if self.new_mandel.has_border:
        #     self.new_mandel.remove_border()

    def _calc_offset(self,
                     previous_shape: tuples.ImageShape,
                     new_shape: tuples.ImageShape,
                     pan: Optional[tuples.PixelPoint] = None) -> tuples.PixelPoint:
        # possibly should be floats, especially if pan is None
        x = int((previous_shape.x - new_shape.x) / 2.0)
        y = int((previous_shape.y - new_shape.y) / 2.0)
        if pan is not None:
            x += pan.x
            y += pan.y
        return tuples.PixelPoint(x, y)

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

    def no_border_and_calc(self):
        self.new_mandel = self.displayed_mandel.lite_copy(
            shape=self._frame_shape,
            has_border=False
        )
        self.calc_new_mandel(save_history=True)
    # endregion

    # region Events from Thread
    def _on_progress_update(self, _: thread.Job, progress: float):
        self._controller.progress_update(progress)

    # def _on_active_change(self, active: bool):
    #     self._worker_active = active

    def _on_stop_success(self):
        self._controller.stop_success()

    def _on_job_complete(self, job: thread.Job):
        # print(f"completed job id = {id(job)}")
        assert isinstance(job, mandelbrot.MandelJob)
        mandel_job: mandelbrot.MandelJob = job
        self.new_mandel = mandel_job.new_mandel
        if mandel_job.progress_estimator:  # only show time for borderless calculation
            self.new_mandel.time_taken = job.progress_estimator.timer.total
        self._controller.new_is_ready(mandel_job.save_history)

        # TODO: control generation of borders in controller rather than automatically firing?
        if not self.new_mandel.has_border:
            self._add_border()

    def _add_border(self):
        border_size = 14*4*10    # add 5 large boxes in all directions
        displayed_shape = self.displayed_mandel.shape
        new_shape = tuples.ImageShape(displayed_shape.x + border_size*2,
                                      displayed_shape.y + border_size*2)
        self.new_mandel = self.displayed_mandel.lite_copy(
            shape=new_shape,
            has_border=True
        )

        offset = tuples.PixelPoint(x=-border_size, y=-border_size)

        job = mandelbrot.MandelJob(
            compute_manager=self._compute_manager,
            new_mandel=self.new_mandel,
            prev_mandel=self.displayed_mandel,
            offset=offset,
            display_progress=False,  # background job
            save_history=False
        )
        self._calc_thread_manager.request_job(job, queue_as=thread.QueueAs.ENQUEUE)
    # endregion

    # region Initial Mandel Options
    def _initial_mandel(self) -> mandelbrot.Mandel:
        mandel = mandelbrot.Mandel(centre=complex(-0.5, 0.0),
                                   size=2.4,
                                   shape=self._frame_shape,
                                   expected_iterations_per_pixel=1750
                                   )
        return mandel

    def _test_mandel(self) -> mandelbrot.Mandel:
        mandel = mandelbrot.Mandel(centre=complex(0.1, 0.1),
                                   size=0.2,
                                   shape=self._frame_shape
                                   )
        return mandel

    def _different_mandel(self) -> mandelbrot.Mandel:
        mandel = mandelbrot.Mandel(centre=complex(-0.745428, 0.113009),
                                   size=3.0E-5,
                                   shape=self._frame_shape
                                   )
        return mandel

    def _slow_mandel(self) -> mandelbrot.Mandel:
        mandel = mandelbrot.Mandel(centre=complex(-0.35980129738448136, 0.6009829289455502),
                                   size=2.1609798031004707e-10,
                                   shape=self._frame_shape
                                   )
        return mandel
    # endregion

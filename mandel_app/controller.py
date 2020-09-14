from __future__ import annotations
from typing import Optional

from mandel_app import model, view, tuples
from mandel_app.model import mandelbrot


class Controller:
    # region Setup
    def __init__(self, model_: model.Model, view_: view.View):
        self._model: model.Model = model_
        self._view: view.View = view_

    def build(self):
        self._view.build()
        self._model.build(self._view.frame_shape)
        self._view.set_calc_thread_state(self._model.calc_thread_state)
        # self._model.start_test_mandel()
        self._model.calc_new_mandel(save_history=True)
    # endregion

    # region Requests from View
    def get_displayed_mandel(self) -> mandelbrot.Mandel:
        return self._model.displayed_mandel

    def get_z0(self) -> complex:
        return self._model.z_model.z0

    def on_resized(self):
        self._model.on_resized(self._view.frame_shape)

    def point_zoom_request(self,
                           pixel_point: Optional[tuples.PixelPoint] = None,
                           scaling: float = 1.0):
        self._model.zoom_and_calc(pixel_point, scaling)

    def back_request(self):
        self._model.restore_previous_as_new()

    def pan_request(self, pan: tuples.PixelPoint):
        self._model.pan_and_calc(pan)

    def rotate_request(self, theta_degrees: int):
        modulated_theta = theta_degrees % 360
        self._model.rotate_and_calc(modulated_theta)

    def stop_request(self):
        self._model.request_stop()
        # self._model.revert_to_displayed_as_new()

    def new_compute_parameters_request(self, max_iterations: Optional[int] = None, early_stopping: bool = True):
        self._model.request_stop()
        # self._model.revert_to_displayed_as_new()
        # could be mid-way but should just stop at next yield
        self._model.set_compute_parameters(max_iterations, early_stopping)
        self._model.no_border_and_calc()
        # if self._model.new_mandel.has_border:
        #     self._model.new_mandel.remove_border()
        # # Save history in case press back don't want to lose the work
        # self._model.calc_new_mandel(save_history=True)

    def perform_default_z_trace(self):
        z0 = self._model.displayed_mandel.centre
        self.perform_z_trace(z0)

    def update_z0_request(self, frame_point: tuples.PixelPoint):
        self._view.hide_z_graph()
        z0 = self._model.displayed_mandel.get_complex_from_frame_point(self._view.frame_shape, frame_point)
        self.perform_z_trace(z0)

    def perform_z_trace(self, z0: complex):
        self._view.show_z0_marker(z0)
        self._model.z_model.build(z0=z0)
        self._view.show_z_graph(self._model.z_model)

    def redraw_z_trace(self, image_shape: tuples.ImageShape):
        self._view.hide_z_graph()
        self._model.z_model.build(image_shape=image_shape)
        self._view.show_z_graph(self._model.z_model)

    def hide_z_trace(self):
        self._view.hide_z0_marker()
        self._view.hide_z_graph()
    # endregion

    # region Notifications from Model
    def progress_update(self, progress: float):
        self._view.display_progress(progress)

    def stop_success(self):
        self._view.stop_success()

    def new_is_ready(self, save_history: bool = False):
        if self._view.ready_to_display_new_mandel:
            # possibly pass an optional z0 in here
            self._view.show_mandel(self._model.new_mandel)
            self._model.new_is_displayed(save_history=save_history)
    # endregion

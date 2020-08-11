from __future__ import annotations
from typing import Optional

from mandel_app import model, view, tuples


class Controller:
    # region Setup
    def __init__(self):
        self._model: Optional[model.Model] = None
        self._view: Optional[view.View] = None

    def set_model(self, model_: model.Model):
        self._model = model_

    def set_view(self, view_: view.View):
        self._view = view_

    def build_and_run(self):
        self._view.build()
        image_space: tuples.ImageShape = self._view.get_image_space()
        self._model.build(image_space)
        # self._model.start_test_mandel()
        self._model.calc_new_mandel(save_history=True)
        self._view.run()
    # endregion

    # region Model notifications
    def progress_update(self, progress: float):
        self._view.display_progress(progress)

    def stop_success(self):
        self._view.stop_success()

    def new_is_ready(self, save_history: bool = False):
        if self._view.ready_to_display_new_mandel:
            self._view.show_mandel(self._model.new_mandel)
            self._model.new_is_displayed(save_history=save_history)
        else:
            self._model.revert_to_displayed_as_new()
    # endregion

    # region View requests
    def point_zoom_request(self,
                           pixel_point: Optional[tuples.PixelPoint] = None,
                           scaling: float = 1.0):
        image_space: tuples.ImageShape = self._view.get_image_space()
        self._model.zoom_and_calc(image_space, pixel_point, scaling)

    def back_request(self):
        self._model.restore_previous_as_new()

    def pan_request(self, pan: tuples.PixelPoint):
        self._model.pan_and_calc(pan)

    def rotate_request(self, theta: int):
        self._model.rotate_and_calc(theta)

    def stop_request(self):
        self._model.request_stop()
        self._model.revert_to_displayed_as_new()

    def new_compute_parameters_request(self, max_iterations: Optional[int] = None, early_stopping: bool = True):
        self._model.request_stop()
        self._model.revert_to_displayed_as_new()
        # could be mid-way but should just stop at next yield
        self._model.set_compute_parameters(max_iterations, early_stopping)
        if self._model.new_mandel.has_border:
            self._model.new_mandel.remove_border()
        # Save history in case press back don't want to lose the work
        self._model.calc_new_mandel(save_history=True)

    def show_z_graph(self):
        self._view.show_z_graph(self._model.z_model)

    def hide_z_graph(self):
        self._view.hide_z_graph()
    # endregion

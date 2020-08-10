from __future__ import annotations

from typing import Optional
import sys

from matplotlib import backend_bases

from PyQt5 import QtCore, QtGui, QtWidgets

from mandel_app import controller, tuples
from mandel_app.model import mandelbrot

from mandel_app.view import window, enums, view_state, icon, z_window


class View:
    # region Setup
    def __init__(self):
        self._controller: Optional[controller.Controller] = None
        self._application: Optional[QtWidgets.QApplication] = None
        self._dock_icon: Optional[icon.Icon] = None
        self._window: Optional[window.Window] = None
        self._z_window: Optional[z_window.ZWindow] = None
        self._view_state: view_state.ViewState = view_state.ViewState()

    def set_controller(self, controller_: controller.Controller):
        self._controller = controller_

    def build(self):
        self._application = QtWidgets.QApplication(sys.argv)
        self._dock_icon = icon.Icon("mandel_icon.png")
        self._application.setWindowIcon(self._dock_icon.q_icon)
        self._window = window.Window()
        self._window.central.mandel_image.set_cursor(self._view_state.cursor_shape)
        self._z_window = z_window.ZWindow(self._window.q_main_window)

        self._connect_signals()
    # endregion

    # region Controller Messages
    def get_image_space(self) -> tuples.ImageShape:
        return self._window.central.image_space

    def run(self):
        sys.exit(self._application.exec_())

    @property
    def ready_to_display_new_mandel(self) -> bool:
        return self._view_state.ready_to_display_new_mandel

    def show_mandel(self, mandel: mandelbrot.Mandel):
        self._set_action(enums.ImageAction.DRAWING)
        # print(f"show_mandel")
        # import time
        # time.sleep(5)
        self._window.central.show_mandel(mandel)
        if not mandel.has_border:
            self._window.toolbars.dial.set_value(mandel.theta_degrees)
            self._window.status_bar.complete(mandel.time_taken)
        self._window.status_bar.q_progress_bar.setVisible(False)
        self._view_state.reset()
        # let other events fire such as mousewheel without acting on them for the new mandel
        # since this wouldn't be what the user wanted
        # enums.ImageAction.DRAWING prevents view acting on most events
        # QtWidgets.QApplication.processEvents()
        self._set_action(enums.ImageAction.NONE)
        # self._window.central.mandel_image.save("mandel_icon.png")

    def display_progress(self, progress: float):
        progress_int_percentage = round(100*progress)
        self._window.status_bar.q_progress_bar.setValue(progress_int_percentage)
        self._window.status_bar.q_progress_bar.setVisible(True)

    def stop_success(self):
        self.show_mandel(self._window.central.mandel_image.mandel)
        # self._window.status_bar.q_progress_bar.setVisible(False)
        # self._set_action(enums.ImageAction.NONE)
    # endregion

    # region Event Connections
    def _connect_signals(self):
        self._connect_escape()
        self._connect_full_screen()
        self._connect_z_mode()
        self._connect_dial_rotate()
        self._connect_iteration()
        self._connect_mandel_image()
        self._window.set_on_key_pressed(self._on_key_pressed)
        self._window.set_on_active(self._on_main_active)
        self._z_window.set_on_active(self._on_z_active)
        self._z_window.set_on_close(self._on_z_close)
        # self._window.set_focus_in_function(self.on_focus_in)
        self._window.central.set_on_resize(self._on_resized)

    def _connect_escape(self):
        self._window.actions.escape.set_on_triggered(on_triggered=self._on_escape)
        self._z_window.actions.escape.set_on_triggered(on_triggered=self._on_escape)

    def _connect_full_screen(self):
        self._window.actions.full_screen.set_on_triggered(on_triggered=self._on_full_screen)
        self._z_window.actions.full_screen.set_on_triggered(on_triggered=self._on_z_full_screen)

    def _connect_z_mode(self):
        self._window.actions.z_mode.set_on_triggered(on_triggered=self._on_set_z_mode)

    def _connect_dial_rotate(self):
        self._window.toolbars.dial.set_on_rotating(on_rotating=self._on_rotating)
        self._window.toolbars.dial.set_on_rotated(on_rotated=self._controller.rotate_request)

    def _connect_iteration(self):
        self._window.actions.max_iterations.set_on_triggered(on_triggered=self._on_max_iteration)
        q_slider = self._window.toolbars.iteration_slider.q_slider
        q_slider.sliderMoved.connect(self._on_iteration_slider_moved)
        q_slider.valueChanged.connect(self._on_iteration_slider_value_changed)

    def _connect_mandel_image(self):
        mandel_image = self._window.central.mandel_image
        mandel_image.add_connection("button_press_event", self._on_mandel_mouse_press)
        mandel_image.add_connection("motion_notify_event", self._on_mandel_mouse_move)
        mandel_image.add_connection("button_release_event", self._on_mandel_mouse_release)
        mandel_image.add_connection("scroll_event", self._on_mandel_mouse_scroll)
    # endregion

    # region General Slots
    def _on_full_screen(self, full_screen: bool):
        self._window.set_full_screen(full_screen)
        if self._view_state.is_z_mode:
            self._z_window.show()

    def _on_z_full_screen(self, _: bool):
        self._window.actions.full_screen.q_action.trigger()

    def _on_rotating(self, to_theta_degrees: int):
        mandel_image = self._window.central.mandel_image
        view_state_ = self._view_state
        if view_state_.ready_to_rotate:
            mandel_image.rotate_mandel_frame(to_theta_degrees)
            self._set_action(enums.ImageAction.ROTATED)

    def _on_max_iteration(self, max_iterations_pressed: bool):
        if max_iterations_pressed:
            self._window.toolbars.slider_visibility(True)
            q_slider = self._window.toolbars.iteration_slider.q_slider
            self._on_iteration_slider_value_changed(q_slider.value())
        else:
            self._window.toolbars.slider_visibility(False)
            self._controller.new_compute_parameters_request()

    def _on_iteration_slider_moved(self, value: int):
        self._display_max_iterations(value)

    def _on_iteration_slider_value_changed(self, value: int):
        max_iterations = self._display_max_iterations(value)
        self._controller.new_compute_parameters_request(max_iterations, early_stopping=False)

    def _on_escape(self, _: bool):
        self._controller.stop_request()

    def _on_key_pressed(self, key_event: QtGui.QKeyEvent):
        key = key_event.key()
        if key == QtCore.Qt.Key_F10:
            print("F10")

    def _on_set_z_mode(self, is_z_mode: bool):
        self._view_state.is_z_mode = is_z_mode
        self._z_window.q_main_window.setVisible(self._view_state.is_z_mode)

    def _on_main_active(self):
        self._window.is_active = True
        self._z_window.is_active = False

    def _on_z_active(self):
        self._z_window.is_active = True
        self._window.is_active = False

    def _on_z_close(self):
        self._window.actions.z_mode.q_action.setChecked(False)

    def _on_resized(self, resize_event: QtGui.QResizeEvent):
        central = self._window.central
        central.set_image_space()
        central.mandel_image.on_resized(central.image_space)

        # have to zoom, ready or not
        self._zoom(scaling=1.0)
    # endregion

    # region MandelImage Slots
    @QtCore.pyqtSlot()
    def _on_mandel_mouse_press(self, event: backend_bases.MouseEvent):
        mandel_image = self._window.central.mandel_image
        view_state_ = self._view_state

        if event.button == backend_bases.MouseButton.LEFT:
            if event.dblclick:
                if view_state_.ready_to_zoom:
                    self._zoom(view_state_.pan_start, scaling=0.1)
            if view_state_.ready_to_pan:
                view_state_.pan_start = mandel_image.get_image_point(event)
                view_state_.pan_end = view_state_.pan_start
                self._set_action(enums.ImageAction.PANNING)
        elif event.button == backend_bases.MouseButton.MIDDLE:
            if view_state_.ready_to_rotate:
                view_state_.rotate_start = mandel_image.get_image_point(event)
                view_state_.mandel_shape = mandel_image.mandel.shape
                self._set_action(enums.ImageAction.ROTATING)
        elif event.button == backend_bases.MouseButton.RIGHT:
            if view_state_.ready_to_zoom:
                if event.dblclick:
                    self._zoom(scaling=10.0)
                else:
                    self._zoom(scaling=2.0)

    @QtCore.pyqtSlot()
    def _on_mandel_mouse_move(self, event: backend_bases.MouseEvent):
        mandel_image = self._window.central.mandel_image
        view_state_ = self._view_state

        if view_state_.action_in_progress == enums.ImageAction.PANNING:
            view_state_.pan_end = mandel_image.get_image_point(event)
            mandel_image.pan_mandel(pan=view_state_.total_pan)
            self._set_action(enums.ImageAction.PANNING)
        elif view_state_.action_in_progress == enums.ImageAction.ROTATING:
            view_state_.rotate_end = mandel_image.get_image_point(event)
            mandel_image.rotate_mandel_mouse(view_state_.total_theta_delta)

    @QtCore.pyqtSlot()
    def _on_mandel_mouse_release(self, event: backend_bases.MouseEvent):
        mandel_image = self._window.central.mandel_image
        view_state_ = self._view_state

        if event.button == backend_bases.MouseButton.LEFT:
            if view_state_.action_in_progress == enums.ImageAction.PANNING:
                view_state_.pan_end = mandel_image.get_image_point(event)
                if view_state_.tiny_pan:
                    # point zoom
                    self._zoom(pixel_point=view_state_.pan_start, scaling=0.5)
                else:
                    new_pan = view_state_.total_pan
                    self._controller.pan_request(new_pan)
                    view_state_.released_pan_delta = new_pan
                    self._set_action(enums.ImageAction.PANNED)

        elif event.button == backend_bases.MouseButton.MIDDLE:
            if view_state_.action_in_progress == enums.ImageAction.ROTATING:
                view_state_.rotate_end = mandel_image.get_image_point(event)
                mouse_theta_delta = view_state_.mouse_theta_delta
                if mouse_theta_delta is not None and mouse_theta_delta != 0:
                    new_theta = mandel_image.mandel.theta_degrees + \
                                view_state_.released_theta_delta + \
                                mouse_theta_delta
                    self._controller.rotate_request(new_theta)
                    view_state_.released_theta_delta = view_state_.released_theta_delta + mouse_theta_delta
                self._set_action(enums.ImageAction.ROTATED)

    @QtCore.pyqtSlot()
    def _on_mandel_mouse_scroll(self, event: backend_bases.MouseEvent):
        mandel_image = self._window.central.mandel_image
        view_state_ = self._view_state
        # print("_on_mandel_mouse_scroll")

        if view_state_.ready_to_zoom:
            # print(f"event.step={event.step}")
            extra_scaling = 0.9 ** float(event.step)
            view_state_.scaling_requested *= extra_scaling
            if event.step > 0:  # zooming in
                cursor = mandel_image.get_image_point(event)
                zoom_point = self._get_zoom_point(cursor)
                self._zoom(zoom_point)
            else:  # zooming out, always just go out, no movement
                self._zoom()
    # endregion

    # region InternalMethods
    def _display_max_iterations(self, power: int) -> int:
        max_iterations = 2 ** power
        self._window.toolbars.set_iterations_label(max_iterations)
        return max_iterations

    def _get_zoom_point(self, cursor: tuples.PixelPoint) -> tuples.PixelPoint:
        return cursor
        # center = self._window.central.mandel_image.center_pixel_point
        # displacement = tuples.PixelPoint(cursor.x - center.x, cursor.y - center.y)
        # zoom_point = tuples.PixelPoint(
        #     x=center.x + 0.5 * displacement.x,
        #     y=center.y + 0.5 * displacement.y
        # )
        # return zoom_point

    def _zoom(self,
              pixel_point: Optional[tuples.PixelPoint] = None,
              scaling: Optional[float] = None):
        mandel_image = self._window.central.mandel_image
        view_state_ = self._view_state

        if scaling is not None:
            view_state_.scaling_requested = scaling

        # if not yet set, then set, else ignore the new pixel point and adjust the zoom on the current point
        if view_state_.scaling_pixel_point is None:
            if pixel_point is None:
                view_state_.scaling_pixel_point = mandel_image.center_pixel_point
            else:
                view_state_.scaling_pixel_point = pixel_point

        pixel_point = view_state_.scaling_pixel_point
        scaling = view_state_.scaling_requested
        # print(f"zoom pixel_point={pixel_point} scaling={scaling:.2f}")
        # import time
        # time.sleep(5)

        mandel_image.zoom_mandel_frame(pixel_point, scaling)
        self._controller.point_zoom_request(pixel_point, scaling)
        self._set_action(enums.ImageAction.ZOOMED)

    def _set_action(self, action: enums.ImageAction):
        self._view_state.action_in_progress = action
        self._window.central.mandel_image.set_cursor(self._view_state.cursor_shape)
    # endregion

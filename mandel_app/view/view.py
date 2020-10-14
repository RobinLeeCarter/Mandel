from __future__ import annotations

from typing import Optional

from PyQt5 import QtCore, QtGui, QtWidgets

# import thread
from mandel_app import controller, tuples, application
from mandel_app.model import mandelbrot, z_model
from mandel_app.view import window, state, settings, z_window, enums
from mandel_app.view.common import icon, clipboard

# import utils


class View:
    # region Setup
    def __init__(self, q_application: QtWidgets.QApplication, application_name: str):
        self._q_application: QtWidgets.QApplication = q_application
        self._application_name: str = application_name
        self._color_theme: str = ""
        self._clipboard: clipboard.Clipboard = clipboard.Clipboard(q_application)
        self._controller: Optional[controller.Controller] = None
        self._window: Optional[window.Window] = None
        self._z_window: Optional[z_window.ZWindow] = None
        self._view_state: state.State = state.State()
        self._settings: settings.Settings = settings.Settings(reset=False)
        # self._timer = utils.Timer()
        # self._timer.start()

    def set_controller(self, controller_: controller.Controller):
        self._controller = controller_

    def build(self):
        self.set_color_theme()
        dock_icon = icon.Icon("mandel_icon.png")
        self._q_application.setWindowIcon(dock_icon.q_icon)
        self._window = window.Window(self._application_name, self._color_theme)
        self._window.build(self._settings.window_settings, self._view_state.cursor_shape)
        self._view_state.set_central(self._window.central)
        self._window.central.set_cursor(self._view_state.cursor_shape)
        self._z_window = z_window.ZWindow(self._window.q_main_window, self._color_theme)
        self._z_window.build(self._settings.z_window_settings)

        self._connect_signals()

    def set_color_theme(self):
        app = application.Application.instance()
        if app.os == "Windows":
            self._color_theme = "default"
        elif app.os == "Darwin":    # untested
            self._color_theme = "default"
        elif app.os == "Linux":
            self._color_theme = "darkGray"
    # endregion

    # region Properties
    # properties exposing part of Model that View needs rather than View holding & updating it's own reference
    @property
    def _displayed_mandel(self) -> mandelbrot.Mandel:
        return self._controller.get_displayed_mandel()

    @property
    def _z0(self) -> complex:
        return self._controller.get_z0()

    # other properties that are better calculated in one place
    @property
    def frame_shape(self) -> Optional[tuples.ImageShape]:
        return self._window.central.frame_shape

    @property
    def z_frame_shape(self) -> Optional[tuples.ImageShape]:
        return self._z_window.central.frame_shape

    @property
    def center_frame_point(self) -> Optional[tuples.ImageShape]:
        frame_shape = self.frame_shape
        if frame_shape is None:
            return None
        else:
            center_frame_point = tuples.PixelPoint(
                x=(self.frame_shape.x-1) * 0.5,
                y=(self.frame_shape.y-1) * 0.5
            )
            return center_frame_point

    @property
    def ready_to_display_new_mandel(self) -> bool:
        return self._view_state.ready_to_display_new_mandel
    # endregion

    # region Controller Messages
    def show_mandel(self, mandel: mandelbrot.Mandel):
        self._set_action(enums.ImageAction.DRAWING)
        # print(f"show_mandel")
        # import time
        # time.sleep(5)
        if self._view_state.is_z_mode:
            self._set_z0_marker(self._z0, mandel)
        self._window.central.show_mandel(mandel)
        if not mandel.has_border:
            self._window.toolbars.dial.set_value(mandel.theta_degrees)
            self._window.status_bar.display_time_taken(mandel.time_taken)
            self._window.status_bar.refresh_mandel_statistics(mandel)
        # self._window.status_bar.q_progress_bar.setVisible(False)
        self._view_state.reset()
        # let other events fire such as mousewheel without acting on them for the new mandel
        # since this wouldn't be what the user wanted
        # enums.ImageAction.DRAWING prevents view acting on most events
        # QtWidgets.QApplication.processEvents()
        self._set_action(enums.ImageAction.NONE)
        # self._window.central.save_source("julia_icon.png")
        # self._timer.stop()
        # self._timer.start()

    def display_progress(self, progress: float):
        self._window.status_bar.display_progress(progress)
        # self._timer.lap(f"{progress:.4f}", show=True)

    def stop_success(self):
        # print("stopped")
        # cp.cuda.get_current_stream().synchronize()
        # stream_done = cp.cuda.get_current_stream().done
        # worker_ready = not self._controller._model.calc_thread_state.worker_active
        # print(f"Stream.done: {stream_done}")
        # print(f"worker_ready: {worker_ready}")
        # print(f"self._view_state.revert_on_stop: {self._view_state.revert_on_stop}")
        if self._view_state.revert_on_stop:
            # self.show_mandel(self._window.central.mandel)
            self.show_mandel(self._displayed_mandel)

    def show_z_graph(self, z_model_: z_model.ZModel):
        self._z_window.central.show_graph(z_model_)
        self._z_window.q_main_window.raise_()

    def hide_z_graph(self):
        self._z_window.central.hide_graph()

    def show_z0_marker(self, z0: complex):
        source_point = self._displayed_mandel.get_source_point_from_complex(z0)
        self._window.central.show_z0_marker(source_point)

    def _set_z0_marker(self, z0: complex, mandel: mandelbrot.Mandel):
        source_point = mandel.get_source_point_from_complex(z0)
        self._window.central.set_z0_marker(source_point)

    def hide_z0_marker(self):
        self._window.central.hide_z0_marker()
    # endregion

    # region Connect Events
    def _connect_signals(self):
        self._connect_escape()
        self._connect_full_screen()
        self._connect_z_mode()
        self._connect_julia_mode()
        self._connect_dial_rotate()
        self._connect_iteration_slider()
        self._connect_central_label()
        self._connect_window()
        self._connect_z_window()

    def _connect_escape(self):
        self._window.actions.escape.set_on_triggered(on_triggered=self._on_escape)
        self._z_window.actions.escape.set_on_triggered(on_triggered=self._on_escape)

    def _connect_full_screen(self):
        self._window.actions.full_screen.set_on_triggered(on_triggered=self._on_full_screen)
        self._z_window.actions.full_screen.set_on_triggered(on_triggered=self._on_z_full_screen)

    def _connect_z_mode(self):
        self._window.actions.z_mode.set_on_triggered(on_triggered=self._on_set_z_mode)

    def _connect_julia_mode(self):
        self._window.actions.julia_mode.set_on_triggered(on_triggered=self._on_set_julia_mode)

    def _connect_dial_rotate(self):
        self._window.toolbars.dial.set_on_rotating(on_rotating=self._on_rotating)
        # self._window.toolbars.dial.set_on_rotated(on_rotated=self._controller.rotate_request)
        self._window.toolbars.dial.set_on_rotated(on_rotated=self._on_rotated)

    def _connect_iteration_slider(self):
        self._window.actions.max_iterations.set_on_triggered(on_triggered=self._on_max_iteration)
        x_labelled_slider = self._window.toolbars.iteration_slider.x_labelled_slider
        x_labelled_slider.set_on_slider_moved(self._on_iteration_slider_moved)
        x_labelled_slider.set_on_value_changed(self._on_iteration_slider_value_changed)

    def _connect_window(self):
        q_main_window = self._window.q_main_window
        q_main_window.set_on_key_pressed(self._on_key_pressed)
        q_main_window.set_on_active(self._on_active)
        q_main_window.set_on_resize(self._on_resized)
        q_main_window.set_on_close(self._on_close)
        self._window.status_bar.set_center_on_mouse_press(self._on_copy_press)

    def _connect_z_window(self):
        q_main_window = self._z_window.q_main_window
        q_main_window.set_on_active(self._on_z_active)
        q_main_window.set_on_resize(self._on_z_resized)
        q_main_window.set_on_close(self._on_z_close)

    def _connect_central_label(self):
        x_label = self._window.central.x_label
        x_label.set_on_mouse_press(self._on_central_mouse_press)
        x_label.set_on_mouse_move(self._on_central_mouse_move)
        x_label.set_on_mouse_release(self._on_central_mouse_release)
        x_label.set_on_mouse_double_click(self._on_central_mouse_double_click)
        x_label.set_on_wheel(self._on_central_mouse_wheel)
    # endregion

    # region General Slots
    def _on_full_screen(self, full_screen: bool):
        self._window.set_full_screen(full_screen)
        if self._view_state.is_z_mode:
            self._z_window.show()

    def _on_z_full_screen(self, _: bool):
        self._window.actions.full_screen.q_action.trigger()

    def _on_rotating(self, theta_degrees: int):
        central = self._window.central
        view_state_ = self._view_state
        if view_state_.ready_to_rotate:
            # central.rotate_mandel_frame(theta_degrees)
            theta_delta = theta_degrees - self._displayed_mandel.theta_degrees
            central.rotate_image(theta_delta)
            self._set_action(enums.ImageAction.ROTATED)

    def _on_rotated(self, theta_degrees: int):
        self._controller.rotate_request(theta_degrees)
        self._set_action(enums.ImageAction.ROTATED)

    def _on_max_iteration(self, max_iterations_pressed: bool):
        if max_iterations_pressed:
            self._window.toolbars.slider_visibility(True)
            value = self._window.toolbars.iteration_slider.value
            self._on_iteration_slider_value_changed(value)
        else:
            self._window.toolbars.slider_visibility(False)
            self._controller.new_compute_parameters_request()

    def _on_iteration_slider_moved(self, value: int):
        self._display_max_iterations(value)

    def _on_iteration_slider_value_changed(self, value: int):
        max_iterations = self._display_max_iterations(value)
        self._controller.new_compute_parameters_request(max_iterations, early_stopping=False)

    def _on_escape(self, _: bool):
        self._view_state.revert_on_stop = True
        self._controller.stop_request()

    def _on_key_pressed(self, key_event: QtGui.QKeyEvent):
        key = key_event.key()
        if key == QtCore.Qt.Key_F10:
            print("F10")

    def _on_set_z_mode(self, is_z_mode: bool):
        if is_z_mode:
            self._controller.perform_default_z_trace()
        else:
            self._controller.hide_z_trace()
        self._view_state.is_z_mode = is_z_mode
        self._z_window.q_main_window.setVisible(is_z_mode)
        self._update_cursor()

    def _on_set_julia_mode(self, is_julia_mode: bool):
        if is_julia_mode:
            # disable z_mode
            self._window.actions.z_mode.q_action.setChecked(False)
            # create julia set for selected point
            self._controller.julia_request()
        else:
            # return to previous_mandlebrot
            pass
            # self._controller.hide_z_trace()
        self._view_state.is_julia_mode = is_julia_mode

    def _on_active(self):
        # print("_on_main_active")
        self._window.is_active = True
        self._z_window.is_active = False

    def _on_z_active(self):
        # print("_on_z_active")
        self._z_window.is_active = True
        self._window.is_active = False

    def _on_z_close(self, close_event: QtGui.QCloseEvent):
        if close_event.spontaneous():
            self._settings.write_z_window_settings(self._z_window.q_main_window)
            q_action = self._window.actions.z_mode.q_action
            if q_action.isChecked():
                q_action.trigger()

    def _on_resized(self):
        self._window.central.on_resized()
        # resize, ready or not
        self._controller.on_resized()
        self._set_action(enums.ImageAction.RESIZED)
        # self._zoom(scaling=1.0)

    def _on_z_resized(self):
        z_central = self._z_window.central
        z_central.refresh_image_space()
        image_shape: tuples.ImageShape = z_central.canvas.on_resized(z_central.frame_shape)
        self._controller.redraw_z_trace(image_shape)

    def _on_close(self):
        self._controller.stop_request()
        if self._z_window.q_main_window.isVisible():
            self._settings.write_z_window_settings(self._z_window.q_main_window)
        self._settings.write_window_settings(self._window.q_main_window)

    def _on_copy_press(self, _: QtGui.QMouseEvent):
        text = self._window.status_bar.verbose_mandel_statistics
        self._clipboard.copy_text(text)
        self._window.central.overlay.show_copy_message()
    # endregion

    # region Central Mouse Slots
    def _on_central_mouse_press(self, event: QtGui.QMouseEvent):
        # print("_on_central_mouse_press")
        # add to always request a stop any current GPU work to free it up for scrolling
        view_state_ = self._view_state
        button: QtCore.Qt.MouseButton = event.button()
        if button == QtCore.Qt.LeftButton:
            if view_state_.ready_to_pan:
                self._controller.stop_request()
                view_state_.pan_start = self._mouse_frame_point(event)
                view_state_.pan_end = view_state_.pan_start
                self._set_action(enums.ImageAction.PANNING)
        elif button == QtCore.Qt.MiddleButton:
            if view_state_.ready_to_rotate:
                self._controller.stop_request()
                view_state_.rotate_start = self._mouse_frame_point(event)
                # view_state_.mandel_shape = self._window.central.mandel.shape change
                self._set_action(enums.ImageAction.ROTATING)
        elif button == QtCore.Qt.RightButton:
            if view_state_.ready_to_zoom:
                self._controller.stop_request()
                self._zoom(scaling=2.0)

    def _on_central_mouse_move(self, event: QtGui.QMouseEvent):
        # print("_on_central_mouse_move")
        view_state_ = self._view_state
        central = self._window.central
        # if view_state_.is_waiting and central.mandel is not None:
        if view_state_.is_waiting and self._displayed_mandel is not None:
            frame_point: tuples.PixelPoint = self._mouse_frame_point(event)
            # z: complex = central.mandel.get_complex_from_frame_point(self.frame_shape, frame_point)
            z: complex = self._displayed_mandel.get_complex_from_frame_point(self.frame_shape, frame_point)
            self._window.status_bar.display_point(z)
        elif view_state_.action_in_progress == enums.ImageAction.PANNING:
            view_state_.pan_end = self._mouse_frame_point(event)
            # stream_done = cp.cuda.get_current_stream().done
            # worker_ready = not self._controller._model.calc_thread_state.worker_active
            # print(view_state_.total_pan)
            # if stream_done and worker_ready:
            #     central.pan_image(pan=view_state_.total_pan)
            central.pan_image(pan=view_state_.total_pan)
            self._update_cursor()
        elif view_state_.action_in_progress == enums.ImageAction.ROTATING:
            view_state_.rotate_end = self._mouse_frame_point(event)
            central.rotate_image(view_state_.total_theta_delta)

    def _on_central_mouse_release(self, event: QtGui.QMouseEvent):
        # print("_on_central_mouse_release")
        view_state_ = self._view_state
        central = self._window.central

        # if event.button == backend_bases.MouseButton.LEFT:
        if view_state_.action_in_progress == enums.ImageAction.PANNING:
            view_state_.pan_end = self._mouse_frame_point(event)
            if view_state_.tiny_pan:
                if view_state_.is_z_mode:
                    # change z0 for z-tracing
                    # print(f"clicked at: {view_state_.pan_start}")
                    self._update_z0(frame_point=view_state_.pan_start)
                else:
                    # point zoom
                    self._zoom(frame_point=view_state_.pan_start, scaling=0.5)
            else:
                new_pan = view_state_.total_pan
                central.pan_image(pan=new_pan)
                self._controller.pan_request(new_pan)
                view_state_.released_pan_delta = new_pan
                self._set_action(enums.ImageAction.PANNED)

        # elif event.button == backend_bases.MouseButton.MIDDLE:
        elif view_state_.action_in_progress == enums.ImageAction.ROTATING:
            view_state_.rotate_end = self._mouse_frame_point(event)
            mouse_theta_delta = view_state_.mouse_theta_delta
            if mouse_theta_delta is not None and mouse_theta_delta != 0:
                # new_theta = central.mandel.theta_degrees + \
                new_theta = self._displayed_mandel.theta_degrees + \
                            view_state_.released_theta_delta + \
                            mouse_theta_delta
                self._controller.rotate_request(new_theta)
                view_state_.released_theta_delta = view_state_.released_theta_delta + mouse_theta_delta
                self._set_action(enums.ImageAction.ROTATED)
            else:
                # nothing to do
                self._set_action(enums.ImageAction.NONE)

    def _on_central_mouse_double_click(self, event: QtGui.QMouseEvent):
        """
        This will trigger some 200-500ms after the mouse-press event.
        Note that mouse_press and mouse_release will have triggered first and there's no way to avoid that.
        The first click request will have been sent to the controller and model requesting a new mandel
        This new request will interrupt that job. Waiting would slow down the single click noticeable.
        """
        # print("_on_central_mouse_double_click")
        view_state_ = self._view_state
        button: QtCore.Qt.MouseButton = event.button()
        if button == QtCore.Qt.LeftButton:
            if view_state_.ready_to_zoom and not view_state_.is_z_mode:
                self._zoom(view_state_.pan_start, scaling=0.1)
        elif button == QtCore.Qt.RightButton:
            if view_state_.ready_to_zoom:
                self._zoom(scaling=10.0)

    def _on_central_mouse_wheel(self, event: QtGui.QWheelEvent):
        # print("_on_central_mouse_wheel")
        # add to always request a stop any current GPU work to free it up for scrolling
        self._controller.stop_request()
        view_state_ = self._view_state
        steps: float = self._get_scroll_steps(event)
        # print("_on_central_mouse_wheel")

        if view_state_.ready_to_zoom:
            extra_scaling = 0.9 ** steps
            view_state_.scaling_requested *= extra_scaling
            if steps > 0:  # zooming in
                pos = event.pos()
                cursor = self._frame_image_to_frame_cartesian(x=pos.x(), y=pos.y())
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
        # center = self._window.central.canvas.center_pixel_point
        # displacement = tuples.PixelPoint(cursor.x - center.x, cursor.y - center.y)
        # zoom_point = tuples.PixelPoint(
        #     x=center.x + 0.5 * displacement.x,
        #     y=center.y + 0.5 * displacement.y
        # )
        # return zoom_point

    def _zoom(self,
              frame_point: Optional[tuples.PixelPoint] = None,
              scaling: Optional[float] = None):
        central = self._window.central
        view_state_ = self._view_state

        if scaling is not None:
            view_state_.scaling_requested = scaling

        # if not yet set, then set, else ignore the new pixel point and adjust the zoom on the current point
        if view_state_.scaling_frame_point is None:
            if frame_point is None:
                view_state_.scaling_frame_point = self.center_frame_point
            else:
                view_state_.scaling_frame_point = frame_point

        frame_point = view_state_.scaling_frame_point
        scaling = view_state_.scaling_requested
        assert frame_point is not None, "View._zoom frame_point is None"
        assert scaling is not None, "View._zoom scaling is None"
        central.zoom_image(frame_point, scaling)
        self._controller.point_zoom_request(frame_point, scaling)
        self._set_action(enums.ImageAction.ZOOMED)

    def _update_z0(self, frame_point: tuples.PixelPoint):
        self._controller.update_z0_request(frame_point)
        self._set_action(enums.ImageAction.NONE)

    def _set_action(self, action: enums.ImageAction):
        self._view_state.action_in_progress = action
        self._update_cursor()

    def _update_cursor(self):
        self._window.central.set_cursor(self._view_state.cursor_shape)

    def _mouse_frame_point(self, event: QtGui.QMouseEvent) -> tuples.PixelPoint:
        return self._frame_image_to_frame_cartesian(event.x(), event.y())

    def _frame_image_to_frame_cartesian(self, x: int, y: int) -> tuples.PixelPoint:
        frame_y = self._view_state.frame_shape.y
        frame_point = tuples.PixelPoint(x=x, y=frame_y-y)
        return frame_point

    def _get_scroll_steps(self, event: QtGui.QWheelEvent) -> float:
        # see: https://doc.qt.io/qt-5/qwheelevent.html#globalPosition
        degrees: float = float(event.angleDelta().y()) / 8.0
        steps: float = degrees / 15.0
        return steps
    # endregion

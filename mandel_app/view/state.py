from typing import Optional

from PyQt5.QtCore import Qt

from mandel_app import tuples
from mandel_app.view import enums
from mandel_app.view.window import central


class State:
    def __init__(self):
        self._central: Optional[central.Central] = None
        self.is_z_mode: bool = False        # Z-mode button on toolbar depressed
        self.is_julia_mode: bool = False    # Julia-mode button on toolbar depressed

        self._action_in_progress: enums.ImageAction = enums.ImageAction.NONE
        self.pan_start: Optional[tuples.PixelPoint] = None
        self.pan_end: Optional[tuples.PixelPoint] = None

        self.rotate_start: Optional[tuples.PixelPoint] = None
        self.rotate_end: Optional[tuples.PixelPoint] = None

        self.released_pan_delta: Optional[tuples.PixelPoint] = None
        self.released_theta_delta: int = 0

        self.scaling_frame_point: Optional[tuples.PixelPoint] = None
        self.scaling_requested: float = 1.0

        self.revert_on_stop: bool = False

    @property
    def action_in_progress(self) -> enums.ImageAction:
        return self._action_in_progress

    @action_in_progress.setter
    def action_in_progress(self, new_action: enums.ImageAction):
        self._action_in_progress = new_action
        # print(f"new_action: {new_action.__str__()}\t\t revert_on_stop: {self.revert_on_stop}")

    def set_central(self, central_: central.Central):
        self._central = central_

    def reset(self):
        self.released_pan_delta = None
        self.released_theta_delta = 0
        self.scaling_frame_point = None
        self.scaling_requested = 1.0
        self.revert_on_stop = False

    # @property
    # def mandel(self) -> mandelbrot.Mandel:
    #     return self._central.mandel

    @property
    def frame_shape(self) -> tuples.ImageShape:
        return self._central.frame_shape

    @property
    def is_waiting(self) -> bool:
        return self.action_in_progress == enums.ImageAction.NONE

    @property
    def is_rotate(self) -> bool:
        return self.action_in_progress in (enums.ImageAction.ROTATING,
                                           enums.ImageAction.ROTATED)

    @property
    def is_pan(self) -> bool:
        return self.action_in_progress in (enums.ImageAction.PANNING,
                                           enums.ImageAction.PANNED)

    @property
    def is_zoom(self) -> bool:
        return self.action_in_progress == enums.ImageAction.ZOOMED

    @property
    def ready_to_display_new_mandel(self) -> bool:
        return self.action_in_progress in (enums.ImageAction.NONE,
                                           enums.ImageAction.ROTATED,
                                           enums.ImageAction.PANNED,
                                           enums.ImageAction.RESIZED,
                                           enums.ImageAction.ZOOMED,
                                           enums.ImageAction.DRAWING)

    @property
    def is_drawing(self) -> bool:
        return self.action_in_progress == enums.ImageAction.DRAWING

    @property
    def ready_to_rotate(self) -> bool:
        return self.action_in_progress in (enums.ImageAction.NONE,
                                           enums.ImageAction.ROTATED)

    @property
    def ready_to_pan(self) -> bool:
        return self.action_in_progress in (enums.ImageAction.NONE,
                                           enums.ImageAction.PANNED)

    @property
    def ready_to_zoom(self) -> bool:
        return self.action_in_progress in (enums.ImageAction.NONE,
                                           enums.ImageAction.ZOOMED)

    @property
    def mouse_pan_delta(self) -> Optional[tuples.PixelPoint]:
        if self.pan_start is not None and self.pan_end is not None:
            return tuples.PixelPoint(x=self.pan_start.x - self.pan_end.x,
                                     y=self.pan_start.y - self.pan_end.y)
        else:
            return tuples.PixelPoint(0, 0)
            # return None

    @property
    def total_pan(self) -> tuples.PixelPoint:
        if self.released_pan_delta is None:
            return tuples.PixelPoint(x=self.mouse_pan_delta.x,
                                     y=self.mouse_pan_delta.y)
        else:
            return tuples.PixelPoint(x=self.released_pan_delta.x + self.mouse_pan_delta.x,
                                     y=self.released_pan_delta.y + self.mouse_pan_delta.y)

    @property
    def tiny_pan(self) -> bool:
        return tuples.pixel_distance(self.mouse_pan_delta) <= 0

    @property
    def mouse_theta_delta(self) -> Optional[int]:
        if self.rotate_start is not None and self.rotate_end is not None:
            x_size, y_size = self.frame_shape
            x_diff = self.rotate_end.x - self.rotate_start.x
            # y_diff = self.rotate_end.y - self.rotate_start.y
            theta_delta = int(360.0 * float(x_diff) / float(x_size))
            if self.rotate_start.y < y_size / 2:
                theta_delta = -theta_delta
            return theta_delta
        else:
            return None

    @property
    def total_theta_delta(self) -> int:
        mouse_theta_delta = self.mouse_theta_delta
        if mouse_theta_delta is None:
            mouse_theta_delta = 0
        return self.released_theta_delta + mouse_theta_delta

    @property
    def cursor_shape(self) -> Qt.CursorShape:
        if self.is_pan:
            if self.tiny_pan:
                cursor_shape = Qt.CrossCursor
            else:
                cursor_shape = Qt.OpenHandCursor
        elif self.is_rotate:
            cursor_shape = Qt.SizeHorCursor
        else:
            cursor_shape = Qt.CrossCursor
            # if self.is_z_mode:
            #     cursor_shape = Qt.ArrowCursor
            # else:

        return cursor_shape

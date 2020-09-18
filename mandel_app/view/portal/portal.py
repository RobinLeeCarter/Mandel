import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore

import utils
from mandel_app import tuples
from mandel_app.view.portal import canvas_source, canvas_frame, frame, drawable


class Portal:
    TRANSFORM_TIMEOUT_MS: int = 20

    def __init__(self, q_label: QtWidgets.QLabel):
        self._q_label: QtWidgets.QLabel = q_label
        self._frame: frame.Frame = frame.Frame()
        self._canvas_source: canvas_source.CanvasSource = canvas_source.CanvasSource()
        self._canvas_frame: canvas_frame.CanvasFrame = canvas_frame.CanvasFrame()

        self._current_pan: tuples.VectorInt = tuples.VectorInt(0, 0)
        self._request_pan: tuples.VectorInt = tuples.VectorInt(0, 0)
        self._transform_q_timer = QtCore.QTimer(parent=q_label)
        self._transform_q_timer.setSingleShot(True)
        self._transform_q_timer.timeout.connect(self._on_transform_timeout)

        self._timer: utils.Timer = utils.Timer()

    @property
    def frame(self) -> frame.Frame:
        return self._frame

    def set_source_drawable(self, drawable_: drawable.Drawable):
        self._canvas_source.set_drawable(drawable_)
        self._update_offset()

    def set_frame_drawable(self, drawable_: drawable.Drawable):
        self._canvas_frame.set_drawable(drawable_)

    def set_frame_shape(self, frame_shape: tuples.ImageShape):
        # frame_shape = self._canvas_frame.set_area_shape(area_shape)
        current_frame_shape = self._frame.frame_shape
        if current_frame_shape is None or frame_shape != current_frame_shape:
            self._frame.set_frame_shape(frame_shape)
            self._update_offset()

    def prepare_source_and_frame(self):
        """
        draws to the source i.e. creates rgba array
        need to call a display method after this for it to display on screen
        """
        self._canvas_source.draw()
        self._frame.set_source(source=self._canvas_source.rgba_output)
        self._update_offset()

    # this could be pushed down to the drawable if we want it to be calculated differently for different drawables
    def _update_offset(self):
        """Called once canvas or frame is updated"""
        canvas_shape = self._canvas_source.shape
        frame_shape = self._frame.frame_shape
        # print(f"canvas_shape: {canvas_shape}")
        # print(f"frame_shape: {frame_shape}")
        if canvas_shape is not None and frame_shape is not None:
            current_frame_offset = self._frame.offset
            # offset when frame centered in canvas
            offset = tuples.PixelPoint(
                x=int((canvas_shape.x - frame_shape.x) / 2.0),
                y=int((canvas_shape.y - frame_shape.y) / 2.0)
            )

            # print(f"offset: {offset}")
            if current_frame_offset is None or offset != current_frame_offset:
                self._frame.set_offset(offset)

    def display(self):
        # print("display")
        if self._transform_q_timer.isActive():
            self._transform_q_timer.stop()
        self._frame.plain()
        self._draw_frame()
        self._current_pan: tuples.VectorInt = tuples.VectorInt(0, 0)

    def pan_display(self, pan: tuples.PixelPoint, direct: bool = False):
        direct = True
        # print("pan_display")
        self._request_pan = tuples.VectorInt.from_pixel_point(pan)
        # print(f"request_pan: {self._request_pan}")

        if self._transform_q_timer.isActive():
            self._transform_q_timer.stop()

        if direct:
            self._do_pan(self._request_pan)
        else:
            self._smooth_pan()

    def _on_transform_timeout(self):
        # print("_on_transform_timeout")
        self._smooth_pan()

    def _smooth_pan(self):
        max_pan: float = 20.0
        extra_pan: tuples.VectorInt = self._request_pan - self._current_pan
        extra_pan_size: float = extra_pan.size
        # print(f"_smooth_pan extra_pan_size: {extra_pan_size}")
        if extra_pan_size < max_pan:
            self._do_pan(self._request_pan)
        else:
            scale = (max_pan / extra_pan_size)
            # print(f"scale {scale}")
            # print(f"extra_pan {extra_pan}")
            additional: tuples.VectorInt = scale * extra_pan
            # print(f"additional: {additional}")
            # print(f"current_pan: {self._current_pan}")
            smoothed_pan = self._current_pan + additional
            # print(f"smoothed_pan: {smoothed_pan}")
            self._do_pan(smoothed_pan)
            self._transform_q_timer.start(Portal.TRANSFORM_TIMEOUT_MS)

        # max_pan: float = 30.0
        # pan_complete: bool = False
        #
        # # while not pan_complete:
        # pan_diff = tuples.PixelPoint(
        #     x=pan.x - self._prev_pan.x,
        #     y=pan.y - self._prev_pan.y
        # )
        # pan_diff_dist = tuples.pixel_distance(pan_diff)
        # if pan_diff_dist > max_pan:
        #     print(pan_diff_dist)
        #     new_pan = tuples.PixelPoint(
        #         x=self._prev_pan.x + (max_pan / pan_diff_dist) * pan_diff.x,
        #         y=self._prev_pan.y + (max_pan / pan_diff_dist) * pan_diff.y
        #     )
        #     # new_pan = pan
        # else:
        #     new_pan = pan
        #     pan_complete = True
        # print(pan)
        # self._timer.start()

        # self._timer.lap("rgba")

        # self._timer.lap("draw")
        # self._prev_pan = new_pan
        # self._timer.stop()
        # fps = 1.0/self._timer.total
        # print(f"FPS: {1.0 / self._timer.total:.1f}")
        # if fps < 50.0:
        #     print(f"FPS: {1.0/self._timer.total:.1f}")

    def _do_pan(self, pan: tuples.VectorInt):
        # print(f"_do_pan: {pan}")
        self._current_pan = pan
        pan_pixel = tuples.PixelPoint(pan.x, pan.y)
        self._frame.pan(pan_pixel)
        self._draw_frame()

    def rotate_display(self, degrees: float):
        """Over 100fps at 1080p with border"""
        # self._timer.start()
        self._frame.rotate(degrees)
        # self._timer.lap("make frame")
        self._draw_frame()
        # self._timer.stop(show=False)
        # fps = 1.0/self._timer.total
        # if fps < 50.0:
        #     print(f"FPS: {1.0/self._timer.total:.1f}")

    def scale_display(self, scale: float, scale_frame_point: tuples.PixelPoint):
        self._frame.scale(scale, scale_frame_point)
        self._draw_frame()

    def _draw_frame(self):
        # print(f"self._frame.rgba:\t{self._frame.rgba.shape}")
        self._canvas_frame.set_rgba_input(self._frame.rgba)
        self._canvas_frame.draw()
        # self._timer.lap("canvas_frame")
        self._update_label()
        # self._timer.lap("update_label")

    def _update_label(self):
        # print("_update_label")
        q_pixmap: QtGui.QPixmap = self._pixmap_from_numpy_rgba(self._canvas_frame.rgba_output)
        self._q_label.setPixmap(q_pixmap)

    def _pixmap_from_numpy_rgba(self, rgba: np.ndarray) -> QtGui.QPixmap:
        h, w, c = rgba.shape
        q_image: QtGui.QImage = QtGui.QImage(rgba.data, w, h, c * w, QtGui.QImage.Format_RGBA8888)
        q_pixmap: QtGui.QPixmap = QtGui.QPixmap(q_image)
        return q_pixmap

    def source_to_transformed_frame(self, source_point: tuples.PixelPoint):
        return self._frame.source_to_transformed_frame(source_point)

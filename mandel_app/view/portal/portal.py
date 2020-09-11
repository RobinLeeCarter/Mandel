from typing import Optional

import numpy as np
from PyQt5 import QtWidgets, QtGui

import utils
from mandel_app import tuples
from mandel_app.view.portal import canvas_source, canvas_frame, frame, drawable


class Portal:
    def __init__(self, q_label: QtWidgets.QLabel):
        self._q_label: QtWidgets.QLabel = q_label
        self._frame: frame.Frame = frame.Frame()
        self._canvas_source: canvas_source.CanvasSource = canvas_source.CanvasSource()
        self._canvas_frame: canvas_frame.CanvasFrame = canvas_frame.CanvasFrame()
        self._timer: utils.Timer = utils.Timer()

    @property
    def frame(self) -> frame.Frame:
        return self._frame

    def set_drawable_source(self, drawable_: drawable.Drawable):
        self._canvas_source.set_drawable(drawable_)
        self._update_offset()

    def set_drawable_frame(self, drawable_: drawable.Drawable):
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
        self._frame.plain()
        self._draw_frame()

    def pan_display(self, pan: tuples.PixelPoint):
        self._frame.pan(pan)
        self._draw_frame()

    def rotate_display(self, degrees: float):
        """Over 100fps at 1080p with border"""
        self._timer.start()
        self._frame.rotate(degrees)
        # self._timer.lap("make frame")
        self._draw_frame()
        self._timer.stop(show=False)
        print(f"FPS: {1.0/self._timer.total:.1f}")

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

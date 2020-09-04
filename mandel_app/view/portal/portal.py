from typing import Optional

import numpy as np
from PyQt5 import QtWidgets, QtGui

from mandel_app import tuples
from mandel_app.view.portal import canvas, frame, drawable


class Portal:
    def __init__(self, q_label: QtWidgets.QLabel):
        self._q_label: QtWidgets.QLabel = q_label
        self._frame = frame.Frame()
        self._canvas = canvas.Canvas()

    @property
    def frame_shape(self) -> Optional[tuples.ImageShape]:
        return self._frame.shape

    def set_drawable(self, drawable_: drawable.Drawable):
        self._canvas.set_drawable(drawable_)
        self._update_offset()

    def on_resized(self, frame_shape: tuples.ImageShape):
        self.set_frame_shape(frame_shape)
        self.display()

    def set_frame_shape(self, frame_shape: tuples.ImageShape):
        # q_size: QtCore.QSize = self._q_label.size()
        # print(q_size)
        # image_shape = tuples.ImageShape(x=q_size.width(), y=q_size.height())
        current_frame_shape = self._frame.shape
        if current_frame_shape is None or frame_shape != current_frame_shape:
            self._frame.set_frame_shape(frame_shape)
            self._update_offset()

    def draw_drawable(self):
        """
        draws to the source i.e. creates rgba array
        need to call a display method after this for it to display on screen
        """
        self._canvas.draw()
        self._frame.set_source(source=self._canvas.rgba)
        self._update_offset()

    # this could be pushed down to the drawable if we want it to be calculated differently for different drawables
    def _update_offset(self):
        """Called once canvas or frame is updated"""
        canvas_shape = self._canvas.shape
        frame_shape = self._frame.shape
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
        self._update_label()

    def pan_display(self, pan: tuples.PixelPoint):
        self._frame.pan(pan)
        self._update_label()

    def rotate_display(self, degrees: float):
        self._frame.rotate(degrees)
        self._update_label()

    def scale_display(self, scale: float, scale_point: Optional[tuples.PixelPoint] = None):
        self._frame.scale(scale, scale_point)
        self._update_label()

    def _update_label(self):
        # print("_update_label")
        q_pixmap: QtGui.QPixmap = self._pixmap_from_numpy_rgba(self._frame.result_rgba)
        self._q_label.setPixmap(q_pixmap)

    def _pixmap_from_numpy_rgba(self, rgba: np.ndarray) -> QtGui.QPixmap:
        h, w, c = rgba.shape
        q_image: QtGui.QImage = QtGui.QImage(rgba.data, w, h, c * w, QtGui.QImage.Format_RGBA8888)
        q_pixmap: QtGui.QPixmap = QtGui.QPixmap(q_image)
        return q_pixmap


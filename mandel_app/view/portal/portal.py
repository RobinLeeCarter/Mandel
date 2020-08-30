import numpy as np
from PyQt5 import QtWidgets, QtGui

from mandel_app import tuples
from mandel_app.view.portal import canvas, frame, drawable


class Portal:
    def __init__(self, q_label: QtWidgets.QLabel):
        self._q_label: QtWidgets.QLabel = q_label
        self._frame = frame.Frame()
        self._canvas = canvas.Canvas()

    def set_shape(self, image_shape: tuples.ImageShape):
        self._frame.set_shape(image_shape)

    def set_drawable(self, drawable_: drawable.Drawable):
        self._canvas.set_drawable(drawable_)

    def draw_drawable(self):
        self._canvas.draw()
        self._frame.set_source(self._canvas.rgba)

    def pan_display(self, pan: tuples.PixelPoint):
        self._frame.pan(pan)
        self._update_label()

    def rotate_display(self, degrees: float):
        self._frame.rotate(degrees)
        self._update_label()

    def scale_display(self, scale: float):
        self._frame.scale(scale)
        self._update_label()

    def display(self):
        self._frame.plain()
        self._update_label()

    def _update_label(self):
        q_pixmap: QtGui.QPixmap = self._pixmap_from_numpy_rgba(self._frame.result_rgba)
        self._q_label.setPixmap(q_pixmap)

    def _pixmap_from_numpy_rgba(self, rgba: np.ndarray) -> QtGui.QPixmap:
        h, w, c = rgba.shape
        q_image: QtGui.QImage = QtGui.QImage(rgba.data, w, h, c * w, QtGui.QImage.Format_RGBA8888)
        q_pixmap: QtGui.QPixmap = QtGui.QPixmap(q_image)
        return q_pixmap

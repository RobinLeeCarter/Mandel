from typing import Optional

from PyQt5 import QtWidgets, QtGui, QtCore

from mandel_app import tuples
from mandel_app.model import mandelbrot
from mandel_app.view import widgets, portal
from mandel_app.view.window.central import draw_mandel_source, draw_mandel_frame, overlay, area


class Central:
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        self._area = area.Area(q_main_window)
        self._area.build()
        self.x_label: widgets.XLabel = self._area.portal_label
        self._portal = portal.Portal(self.x_label)
        self._draw_mandel_source = draw_mandel_source.DrawMandelSource()
        self._draw_mandel_frame = draw_mandel_frame.DrawMandelFrame()
        self._portal.set_drawable_source(self._draw_mandel_source)
        self._portal.set_drawable_frame(self._draw_mandel_frame)

        self.overlay = overlay.Overlay(parent=self.x_label)
        self.x_label.set_overlay(self.overlay)

    def build(self, cursor_shape: QtCore.Qt.CursorShape):
        self.set_frame_shape()
        # self._area.refresh_shape()
        # # # print(f"self._area.shape: {self._area.shape}")
        # self._portal.set_frame_shape(self._area.shape)
        self.set_cursor(cursor_shape)

    def on_resized(self):
        # self._area.refresh_shape()
        self.set_frame_shape()
        self._portal.display()
        # self._portal.on_resized(self._area.shape)

    def set_frame_shape(self):
        self._area.refresh_shape()
        self._draw_mandel_frame.set_frame_shape(self._area.shape)
        self._portal.set_frame_shape(self._area.shape)

    def show_mandel(self, mandel: mandelbrot.Mandel):
        """assuming frame size is not changing"""
        self._draw_mandel_source.set_mandel(mandel)
        self._portal.prepare_source_and_frame()
        self._portal.display()

    @property
    def frame_shape(self) -> Optional[tuples.ImageShape]:
        return self._portal.frame_shape

    def rotate_image(self, degrees: int):
        # to rotate image is one direction we need to rotate the frame in the other
        self._portal.rotate_display(-degrees)

    def zoom_image(self,
                   zoom_frame_point: tuples.PixelPoint,
                   scaling: Optional[float] = None):
        if scaling is None:
            scaling = 1.0
        self._portal.scale_display(scaling, zoom_frame_point)

    def pan_image(self, pan: tuples.PixelPoint):
        self._portal.pan_display(pan)

    def show_z0_marker(self, z0: complex):
        self._draw_mandel_frame.set_z0(z0)
        self._portal.prepare_source_and_frame()
        self._portal.display()

    def hide_z0_marker(self):
        self._draw_mandel_frame.hide_z0()
        self._portal.display()

    def set_cursor(self, cursor_shape: QtCore.Qt.CursorShape):
        cursor = QtGui.QCursor(cursor_shape)
        self.x_label.setCursor(cursor)

        # image_shape = self._portal.drawable_shape
        # x_offset = min(int((new_image_shape.x - image_shape.x) / 2.0), 0)
        # y_offset = min(int((new_image_shape.y - image_shape.y) / 2.0), 0)
        # self._mandel_draw.mandel.set_offset(tuples.PixelPoint(x=x_offset, y=y_offset))

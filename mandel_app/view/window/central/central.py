from typing import Optional

from PyQt5 import QtWidgets, QtCore

from mandel_app import tuples
from mandel_app.model import mandelbrot
from mandel_app.view import widgets, portal
from mandel_app.view.window.central import draw_mandel_source, draw_mandel_frame, overlay, scroll_area


class Central:
    # region Setup
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        self._scroll_area = scroll_area.ScrollArea(q_main_window)
        # self._area.build()
        self.x_label: widgets.XLabel = self._scroll_area.portal_label
        self._portal = portal.Portal(self.x_label)
        self._draw_mandel_source = draw_mandel_source.DrawMandelSource()
        self._draw_mandel_frame = draw_mandel_frame.DrawMandelFrame()
        self._portal.set_source_drawable(self._draw_mandel_source)
        self._portal.set_frame_drawable(self._draw_mandel_frame)

        self.overlay = overlay.Overlay(parent=self.x_label)
        self.x_label.set_overlay(self.overlay)

    def build(self, cursor_shape: QtCore.Qt.CursorShape):
        self._draw_mandel_frame.set_frame(self._portal.frame)
        self.set_frame_shape()
        self.set_cursor(cursor_shape)
    # endregion

    def on_resized(self):
        self.set_frame_shape()
        self._portal.display()

    def set_frame_shape(self):
        frame_shape = self._scroll_area.get_shape()
        # print(f"_scroll_area.shape:\t{shape}")
        self._portal.set_frame_shape(frame_shape)

    def show_mandel(self, mandel: mandelbrot.Mandel):
        """assuming frame size is not changing"""
        self._draw_mandel_source.set_mandel(mandel)
        self._portal.prepare_source_and_frame()
        self._portal.display()

    def save_source(self, filename: str):
        self._portal.save_source(filename)

    @property
    def frame_shape(self) -> Optional[tuples.ImageShape]:
        return self._portal.frame.frame_shape

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

    def show_z0_marker(self, source_point: tuples.PixelPoint):
        self.set_z0_marker(source_point)
        # self._portal.prepare_source_and_frame()
        self._portal.display()

    def set_z0_marker(self, source_point: tuples.PixelPoint):
        self._draw_mandel_frame.set_z0_source_point(source_point)

    def hide_z0_marker(self):
        self._draw_mandel_frame.hide_z0()
        self._portal.display()

    def set_cursor(self, cursor_shape: QtCore.Qt.CursorShape):
        self.x_label.set_cursor_shape(cursor_shape)

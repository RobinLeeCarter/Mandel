from typing import Optional

from PyQt5 import QtWidgets, QtGui, QtCore

from mandel_app import tuples
from mandel_app.model import mandelbrot
from mandel_app.view import widgets, portal
from mandel_app.view.window.central import mandel_draw, area, overlay


class Central:
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        self._area = area.Area(q_main_window)
        self.x_label: widgets.XLabel = self._area.portal_label
        self._portal = portal.Portal(self.x_label)
        self._mandel_draw = mandel_draw.MandelDraw()
        self._portal.set_drawable(self._mandel_draw)

        self.overlay = overlay.Overlay(parent=self.x_label)
        self.x_label.set_overlay(self.overlay)

    def show_mandel(self, mandel: mandelbrot.Mandel):
        """assuming frame size is not changing"""
        self._mandel_draw.set_mandel(mandel)
        self._portal.draw_drawable()
        self._portal.display()
        self._area.refresh()

    def refresh_image_space(self):
        self._area.refresh_image_space()

    @property
    def mandel(self) -> mandelbrot.Mandel:
        return self._mandel_draw.mandel

    @property
    def image_shape(self) -> tuples.ImageShape:
        return self._area.image_shape

    @property
    def center_pixel_point(self) -> tuples.PixelPoint:
        mandel = self._mandel_draw.mandel
        return tuples.PixelPoint(mandel.shape.x * 0.5, mandel.shape.y * 0.5)

    def rotate_mandel_mouse(self, total_theta_delta: int):
        self._rotate_mandel(-total_theta_delta)

    def rotate_mandel_frame(self, to_theta_degrees: int):
        mandel = self._mandel_draw.mandel
        # new rotation is required rotation minus current rotation
        theta_delta = to_theta_degrees - mandel.theta_degrees
        # to rotate the frame one direction we must rotate the image in the opposite direction
        degrees = -theta_delta
        self._rotate_mandel(degrees)

    def _rotate_mandel(self, degrees: int):
        self._portal.rotate_display(degrees)
        self._area.refresh()

    def zoom_mandel_frame(self,
                          zoom_point: Optional[tuples.PixelPoint] = None,
                          scaling: Optional[float] = None):
        center = self.center_pixel_point
        if zoom_point is None:
            zoom_point = center

        if scaling is None:
            magnification = 1.0
        else:
            magnification = 1.0 / scaling
        self._portal.scale_display(magnification, zoom_point)
        self._area.refresh()

    def pan_mandel(self, pan: tuples.PixelPoint):
        self._portal.pan_display(pan)
        self._area.refresh()

    def show_z0_marker(self, z0: complex):
        self._mandel_draw.set_z0_marker(z0)
        self._portal.display()

    def hide_z0_marker(self):
        self._mandel_draw.hide_z0_marker()
        self._portal.display()

    def set_cursor(self, cursor_shape: QtCore.Qt.CursorShape):
        cursor = QtGui.QCursor(cursor_shape)
        self.x_label.setCursor(cursor)

    def on_resized(self, new_image_shape: tuples.ImageShape):
        # image_shape = self._portal.drawable_shape
        # x_offset = min(int((new_image_shape.x - image_shape.x) / 2.0), 0)
        # y_offset = min(int((new_image_shape.y - image_shape.y) / 2.0), 0)
        # self._mandel_draw.mandel.set_offset(tuples.PixelPoint(x=x_offset, y=y_offset))
        self._portal.on_resize()

    # def above_center(self, y: int) -> bool:
    #     return y >= self._mandel_draw.mandel.shape.y / 2

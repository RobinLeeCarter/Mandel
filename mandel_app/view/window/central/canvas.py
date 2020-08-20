from __future__ import annotations
from typing import Optional, Callable, List

import numpy as np

import matplotlib
from matplotlib import figure, backend_bases, image, transforms, lines
from matplotlib.backends import backend_qt5agg

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

# import utils
from mandel_app import tuples
from mandel_app.model import mandelbrot
from mandel_app.view.window.central import overlay


IMAGE_PATH = "mandel_app/mandelbrot_images/"


class Canvas:
    def __init__(self):
        # was in learnpyqt tutorial and probably no harm but doesn't seem to do anything
        matplotlib.use('Qt5Agg')
        self._mandel: Optional[mandelbrot.Mandel] = None
        self._dpi: int = self.get_dpi()
        self._fig: figure.Figure = figure.Figure(frameon=False, dpi=self._dpi)
        # Space around axes. Documentation not helpful. Taken from stack-overflow.
        self._fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        self._ax: figure.Axes = self._fig.subplots()
        self._figure_canvas: XFigureCanvasQTAgg = XFigureCanvasQTAgg(self._fig)
        self._ax_image: Optional[image.AxesImage] = None
        self._z0: Optional[complex] = None
        self._z0_marker = lines.Line2D([], [], marker='x', markersize=30, color="blue",
                                       zorder=1, visible=False)
        self._connections = {}

    @property
    def mandel(self) -> Optional[mandelbrot.Mandel]:
        return self._mandel

    @property
    def figure_canvas(self) -> XFigureCanvasQTAgg:
        return self._figure_canvas

    @property
    def center_pixel_point(self) -> tuples.PixelPoint:
        return tuples.PixelPoint(self._mandel.shape.x * 0.5, self._mandel.shape.y * 0.5)

    def get_dpi(self) -> int:
        q_application = QtWidgets.QApplication.instance()   # get singleton
        screen: QtGui.QScreen = q_application.screens()[0]
        dpi = round(screen.physicalDotsPerInch())
        # print(f"dpi = {dpi}")
        return dpi

    def draw_mandel(self, mandel_: mandelbrot.Mandel):
        self._mandel = mandel_
        # 7ms could potentially go faster with a lookup
        transformed_iterations = 100*np.mod(np.log10(1 + self._mandel.iteration), 1)
        transformed_iterations[self._mandel.iteration == self._mandel.max_iteration] = 0

        self.figure_canvas.resize(self._mandel.shape.x, self._mandel.shape.y)
        self._ax.clear()
        # don't appear to do anything with fig.subplots_adjust set
        self._ax.set_axis_off()
        self._ax.margins(0, 0)
        self._ax_image: image.AxesImage = self._ax.imshow(
            transformed_iterations,
            interpolation='none', origin='lower',
            cmap='hot', vmin=0, vmax=100, alpha=1.0, zorder=0)
        self._ax.add_line(self._z0_marker)
        if self._z0 is not None:
            self._set_z0_marker()

        # self.figure_canvas.draw()
        self._transform_and_draw()

    def rotate_mandel_mouse(self, total_theta_delta: int):
        self._rotate_mandel(-total_theta_delta)

    def rotate_mandel_frame(self, to_theta_degrees: int):
        # new rotation is required rotation minus current rotation
        theta_delta = to_theta_degrees - self._mandel.theta_degrees
        # to rotate the frame one direction we must rotate the image in the opposite direction
        degrees = -theta_delta
        self._rotate_mandel(degrees)

    def _rotate_mandel(self, degrees: int):
        centre = self.center_pixel_point
        transform = transforms.Affine2D() \
            .translate(-centre.x, -centre.y) \
            .rotate_deg(degrees) \
            .translate(centre.x, centre.y)
        self._transform_and_draw(transform)

    def zoom_mandel_frame(self,
                          zoom_point: Optional[tuples.PixelPoint] = None,
                          scaling: Optional[float] = None):
        centre = self.center_pixel_point
        if zoom_point is None:
            zoom_point = self.center_pixel_point
        if scaling is None:
            magnification = 1.0
        else:
            magnification = 1.0 / scaling

        transform = transforms.Affine2D() \
            .translate(-zoom_point.x, -zoom_point.y) \
            .scale(magnification) \
            .translate(centre.x, centre.y)
        self._transform_and_draw(transform)

    def pan_mandel(self, pan: tuples.PixelPoint):
        transform = transforms.Affine2D().translate(-pan.x, -pan.y)
        self._transform_and_draw(transform)

    def _transform_and_draw(self, transform: Optional[transforms.Affine2D] = None):
        if transform is None:  # no transformation, just draw
            transform = transforms.Affine2D()
        # widget places image in top left. Our co-ordinate system is bottom right.
        if self._mandel.offset != tuples.PixelPoint(0, 0):
            transform = transform.translate(self._mandel.offset.x, -self._mandel.offset.y)
        trans_data = transform + self._ax.transData
        self._ax_image.set_transform(trans_data)
        self._z0_marker.set_transform(trans_data)
        # self.ax.add_line(self._z0_marker)
        # self.ax.plot([0.1], [0.1], marker='x', markersize=10, color="blue", zorder=10)
        self.figure_canvas.draw()

    def show_z0_marker(self, z0: complex):
        self._z0 = z0
        self._set_z0_marker()
        self.figure_canvas.draw()

    def _set_z0_marker(self):
        pixel_x: List[int] = []
        pixel_y: List[int] = []
        pixel_point: Optional[tuples.PixelPoint] = self._mandel.get_pixel_from_complex(self._z0)
        if pixel_point is not None:
            pixel_x.append(pixel_point.x)
            pixel_y.append(pixel_point.y)
            # self._z0_marker.set_data([pixel_point.x], [pixel_point.y])
        self._z0_marker.set_data(pixel_x, pixel_y)
        self._z0_marker.set_visible(True)

    def hide_z0_marker(self):
        self._z0 = None
        self._z0_marker.set_visible(False)
        self.figure_canvas.draw()

    def save(self, file_path: str):
        self._fig.savefig(IMAGE_PATH + file_path, format="png",
                          pad_inches=0, bbox_inches='tight', transparent=True, dpi=self._dpi)

    #     """See: https://matplotlib.org/3.1.1/users/event_handling.html"""
    def add_connection(self, event_name: str, func: Callable[[backend_bases.Event], None]):
        connection_id = self.figure_canvas.mpl_connect(event_name, func)
        self._connections[event_name] = connection_id

    def remove_connection(self, event_name: str):
        connection_id = self._connections[event_name]
        self.figure_canvas.mpl_disconnect(connection_id)

    def set_cursor(self, cursor_shape: Qt.CursorShape):
        cursor = QtGui.QCursor(cursor_shape)
        self.figure_canvas.setCursor(cursor)

    def on_resized(self, new_image_space: tuples.ImageShape):
        image_shape = self._mandel.shape
        x_offset = min(int((new_image_space.x - image_shape.x) / 2.0), 0)
        y_offset = min(int((new_image_space.y - image_shape.y) / 2.0), 0)
        self._mandel.offset = tuples.PixelPoint(x=x_offset, y=y_offset)
        self._transform_and_draw()

    # with the image offset, event gives an odd x, y position.
    # this function converts it back to a sensible one
    def get_image_point(self, event: backend_bases.MouseEvent):
        image_point = tuples.PixelPoint(x=event.x - self._mandel.offset.x,
                                        y=event.y + self._mandel.offset.y)
        return image_point

    def above_center(self, y: int) -> bool:
        return y >= self._mandel.shape.y / 2


class XFigureCanvasQTAgg(backend_qt5agg.FigureCanvasQTAgg):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._overlay: Optional[overlay.Overlay] = None

    def set_overlay(self, overlay_: overlay.Overlay):
        self._overlay = overlay_

    def paintEvent(self, q_paint_event: QtGui.QPaintEvent):
        super().paintEvent(q_paint_event)
        self._overlay.draw(q_paint_event)

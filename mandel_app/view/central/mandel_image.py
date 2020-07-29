from typing import Optional, Callable

import numpy as np

import matplotlib
from matplotlib import figure, backend_bases, image, transforms
from matplotlib.backends import backend_qt5agg

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

# import utils
from mandel_app import tuples
from mandel_app.model import mandelbrot


IMAGE_PATH = "mandel_app/mandelbrot_images/"


class MandelImage:
    def __init__(self):
        # was in learnpyqt tutorial and probably no harm but doesn't seem to do anything
        matplotlib.use('Qt5Agg')
        self.mandel: Optional[mandelbrot.Mandel] = None
        self.dpi = self.get_dpi()
        self.fig: figure.Figure = figure.Figure(frameon=False, dpi=self.dpi)
        # Space around axes. Documentation not helpful. Taken from stack-overflow.
        self.fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        self.ax: figure.Axes = self.fig.subplots()
        self.mandel_canvas = backend_qt5agg.FigureCanvasQTAgg(self.fig)
        self.ax_image: Optional[image.AxesImage] = None

        self.connections = {}

    def get_dpi(self):
        q_application = QtWidgets.QApplication.instance()   # get singleton
        screen: QtGui.QScreen = q_application.screens()[0]
        dpi = round(screen.physicalDotsPerInch())
        # print(f"dpi = {dpi}")
        return dpi

    def draw_mandel(self, mandel_: mandelbrot.Mandel):
        self.mandel = mandel_
        # 7ms could potentially go faster with a lookup
        transformed_iterations = 100*np.mod(np.log10(1+self.mandel.iteration), 1)
        transformed_iterations[self.mandel.iteration == self.mandel.max_iteration] = 0

        self.mandel_canvas.resize(self.mandel.shape.x, self.mandel.shape.y)
        self.ax.clear()
        # don't appear to do anything with fig.subplots_adjust set
        self.ax.set_axis_off()
        self.ax.margins(0, 0)
        self.ax_image: image.AxesImage = self.ax.imshow(
            transformed_iterations,
            interpolation='none', origin='lower',
            cmap='hot', vmin=0, vmax=100)

        self._transform_and_draw()

    def rotate_mandel_mouse(self, total_theta_delta: int):
        self._transform_and_draw(degrees=-1*total_theta_delta)

    def rotate_mandel_frame(self, to_theta_degrees: int):
        theta_delta = to_theta_degrees - self.mandel.theta_degrees
        if theta_delta != 0:
            # self.action_in_progress = enums.ImageAction.ROTATING
            # to rotate frame one way we must rotate the image in the other
            self._transform_and_draw(degrees=-theta_delta)

    def pan_mandel_frame(self, pan: tuples.PixelPoint):
        self._transform_and_draw(pan=pan)

    def _transform_and_draw(self, degrees: int = 0, pan: tuples.PixelPoint = None):
        transform = transforms.Affine2D()
        # perform any rotation
        # if self.action_in_progress == enums.ImageAction.ROTATING and degrees != 0:
        if degrees != 0:
            centre_x = int(float(self.mandel.shape.x) / 2.0)
            centre_y = int(float(self.mandel.shape.y) / 2.0)
            transform = transform \
                .translate(-centre_x, -centre_y) \
                .rotate_deg(degrees) \
                .translate(centre_x, centre_y)
        # perform any pan
        # if self.action_in_progress == enums.ImageAction.PANNING and pan != tuples.PixelPoint(0, 0):
        elif pan and not None and pan != tuples.PixelPoint(0, 0):
            transform = transform.translate(-pan.x, -pan.y)
        # centre centre_point of image in widget.
        # widget places image in top left. Our co-ordinate system is bottom right.
        if self.mandel.offset != tuples.PixelPoint(0, 0):
            transform = transform.translate(self.mandel.offset.x, -self.mandel.offset.y)
        trans_data = transform + self.ax.transData
        self.ax_image.set_transform(trans_data)
        self.mandel_canvas.draw()

    def save(self, file_path: str):
        self.fig.savefig(IMAGE_PATH + file_path, format="png",
                         pad_inches=0, bbox_inches='tight', transparent=True, dpi=self.dpi)

    #     """See: https://matplotlib.org/3.1.1/users/event_handling.html"""
    def add_connection(self, event_name: str, func: Callable[[backend_bases.Event], None]):
        connection_id = self.mandel_canvas.mpl_connect(event_name, func)
        # print(connection_id, event_name)
        self.connections[event_name] = connection_id

    def remove_connection(self, event_name: str):
        connection_id = self.connections[event_name]
        self.mandel_canvas.mpl_disconnect(connection_id)

    def set_cursor(self, cursor_shape: Qt.CursorShape):
        cursor = QtGui.QCursor(cursor_shape)
        self.mandel_canvas.setCursor(cursor)

    def on_resized(self, new_image_space: tuples.ImageShape):
        image_shape = self.mandel.shape
        x_offset = min(int((new_image_space.x - image_shape.x) / 2.0), 0)
        y_offset = min(int((new_image_space.y - image_shape.y) / 2.0), 0)
        self.mandel.offset = tuples.PixelPoint(x=x_offset, y=y_offset)
        self._transform_and_draw()

    # with the image offset, event gives an odd x, y position.
    # this function converts it back to a sensible one
    def get_image_point(self, event: backend_bases.MouseEvent):
        image_point = tuples.PixelPoint(x=event.x - self.mandel.offset.x,
                                        y=event.y + self.mandel.offset.y)
        # print(f"image_point = {image_point}")
        return image_point

    def above_center(self, y: int) -> bool:
        return y >= self.mandel.shape.y / 2

    # def set_focus(self):
    #     self.mandel_canvas.setFocus()

    # fig_width_in_inches: float = float(self.shape.x) / float(self.dpi)
    # fig_height_in_inches: float = float(self.shape.y) / float(self.dpi)
    # print(f"fig {fig_width_in_inches}, {fig_height_in_inches}")
    # self.fig.set_size_inches(w=fig_width_in_inches, h=fig_height_in_inches)
    # self.ax.xaxis.set_major_locator(ticker.NullLocator())  possibly unnecesary
    # self.ax.yaxis.set_major_locator(ticker.NullLocator())



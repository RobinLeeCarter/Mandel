from __future__ import annotations
from typing import Optional, Callable, List

import numpy as np

import matplotlib
from matplotlib import figure, backend_bases, image, transforms, lines, cm, colors

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

import utils
from mandel_app import tuples
from mandel_app.model import mandelbrot
from mandel_app.view import widgets
from mandel_app.view.window.central.old import transform

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
        self._figure_canvas: widgets.XFigureCanvasQTAgg =\
            widgets.XFigureCanvasQTAgg(self._fig)

        # TODO: possibly remove
        self._cmap = cm.get_cmap("hot")
        self._cmap.set_bad("pink", alpha=0.0)
        self._norm = colors.Normalize(vmin=0, vmax=1)

        self._ax_image: Optional[image.AxesImage] = None
        self._z0: Optional[complex] = None
        self._z0_marker = lines.Line2D([], [], marker='x', markersize=30, color="blue",
                                       zorder=1, visible=False)
        self._connections = {}

        self._timer = utils.Timer()
        self._transformed_iterations: np.ndarray
        self._transform: transform.Transform = transform.Transform()
        cmap: colors.Colormap = cm.get_cmap("hot")
        # cmap = colors.Colormap("hot")
        self._transform.set_cmap(cmap)
        self._frame_rgba: Optional[np.ndarray] = None

    @property
    def mandel(self) -> Optional[mandelbrot.Mandel]:
        return self._mandel

    @property
    def figure_canvas(self) -> widgets.XFigureCanvasQTAgg:
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

        # self.x_shape = self._mandel.shape.x
        # self.y_shape = self._mandel.shape.y
        #
        # self.canvas = np.zeros(shape=(self.x_shape, self.y_shape, 2), dtype=np.float32)
        #
        # x_pixels = np.arange(start=0, stop=self.x_shape, step=1, dtype=np.float32)
        # y_pixels = np.arange(start=0, stop=self.y_shape, step=1, dtype=np.float32)
        #
        # # xx, yy = np.meshgrid(x, y, indexing='ij')
        # #
        # # f[:, :, 0], f[:, :, 1] = xx, yy
        #
        # self.canvas[:, :, 0], self.canvas[:, :, 1] = np.meshgrid(x_pixels, y_pixels, indexing='ij')

        # TODO: set this separately on resize and to the central shape not to the mandel shape
        self._transform.set_frame_shape(self._mandel.shape)

        self.figure_canvas.resize(self._mandel.shape.x, self._mandel.shape.y)
        self._ax.clear()
        # don't appear to do anything with fig.subplots_adjust set
        self._ax.set_axis_off()
        self._ax.margins(0, 0)

        timer_str = f"initial\tborder: {self._mandel.has_border}"
        self._timer.start()

        self._transform.set_mandel(self._mandel)
        self._frame_rgba = self._transform.get_frame()

        # 7ms could potentially go faster with a lookup
        self.transformed_iterations = 100*np.mod(np.log10(1 + self._mandel.iteration), 1)
        self.transformed_iterations[self._mandel.iteration == self._mandel.max_iteration] = 0

        # self.mod_log_iterations = 100*np.mod(np.log10(1 + self._mandel.iteration), 1)
        # self.mod_log_iterations[self._mandel.iteration == self._mandel.max_iteration] = 0
        #
        # self._norm.autoscale(self.mod_log_iterations)
        # self.normalised = self._norm(self.mod_log_iterations)
        # self.rgba = self._cmap(self.normalised, bytes=True)
        # # self.rgba = self._cmap(self.mod_log_iterations, bytes=True)
        #
        # print(f"self._mandel.iteration.shape {self._mandel.iteration.shape}")
        # # print(f"self.transformed_iterations.shape {self.transformed_iterations.shape}")
        # print(f"self.mod_log_iterations.shape {self.mod_log_iterations.shape}")
        # # print(f"self.normalised.shape {self.normalised.shape}")
        # print(f"self.rgba.shape {self.rgba.shape}")

        # transformed_iterations[self._mandel.iteration == 4] = np.nan
        # transformed_iterations[self._mandel.iteration == 6] = np.nan
        # transformed_iterations[self._mandel.iteration == self._mandel.max_iteration] = 500

        self._ax_image: image.AxesImage = self._ax.imshow(
            self.transformed_iterations,
            interpolation='none', origin='lower',
            cmap=self._cmap, vmin=0, vmax=100, alpha=1.0, zorder=0)

        # self._ax_image2: image.AxesImage = self._ax.imshow(
        #     self._frame_rgba,
        #     interpolation='none', origin='lower', resample=False)
        # self._ax_image2: image.AxesImage = self._ax.imshow(
        #     self._frame_rgba,
        #     interpolation='none', origin='lower', resample=False, filternorm=False)

        # TODO: re-include z0 marker
        # self._ax.add_line(self._z0_marker)
        # if self._z0 is not None:
        #     self._set_z0_marker()

        self.figure_canvas.draw()
        # self._transform_and_draw()

        self._timer.stop(name=timer_str, show=True)

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
        timer_str = f"pan\tborder: {self._mandel.has_border}"
        self._timer.start()
        transform = transforms.Affine2D().translate(-pan.x, -pan.y)
        self._transform_and_draw(transform)
        self._timer.stop(name=timer_str, show=True)

    def pan_mandel_new(self, pan: tuples.PixelPoint):
        # timer_str = f"pan new\tborder: {self._mandel.has_border}"
        self._timer.start()
        self._frame_rgba = self._transform.pan(pan)
        self._timer.lap("generate")
        self._ax_image2.set_data(self._frame_rgba)
        self._timer.lap("set_data")
        # self._ax_image2.remove()
        # self._ax_image2: image.AxesImage = self._ax.imshow(
        #     self._frame_rgba,
        #     interpolation='none', origin='lower', resample=False)
        self.figure_canvas.draw()
        self._timer.lap("display")
        self._timer.stop()

    def pan_mandel2(self, pan: tuples.PixelPoint):
        self.x_shape = self._mandel.shape.x
        self.y_shape = self._mandel.shape.y

        self.canvas = np.zeros(shape=(self.y_shape, self.x_shape, 2), dtype=np.float32)

        x_pixels = np.arange(start=0, stop=self.x_shape, step=1, dtype=np.float32)
        y_pixels = np.arange(start=0, stop=self.y_shape, step=1, dtype=np.float32)

        # xx, yy = np.meshgrid(x, y, indexing='ij')
        #
        # f[:, :, 0], f[:, :, 1] = xx, yy

        self.canvas[:, :, 1], self.canvas[:, :, 0] = np.meshgrid(y_pixels, x_pixels, indexing='ij')

        transform_array = [[0.9, 0.1],
                           [-0.1, 0.9]]

        a = np.array(transform_array, dtype=np.float32)

        # a_transposed = np.zeros(shape=(2, 2), dtype=np.float32)

        a_transposed = a.T

        # frame gives source pixel of each canvas pixel
        frame_float32 = np.matmul(self.canvas, a_transposed)

        # print(frame_float32[1, 2, :])

        frame = np.rint(frame_float32).astype(np.int32)
        frame_x = frame[:, :, 0]
        frame_y = frame[:, :, 1]

        # frame_size_in_mb = (frame.size * frame.itemsize) / (1024 * 1024)
        # print(f"frame size: {frame_size_in_mb:.1f} Mb")

        # print(frame[1, 2, :])

        # source_x_shape = self._mandel.shape.x
        # source_y_shape = self._mandel.shape.y

        # number of iterations in source mandelbrot array
        source = self.rgba
        print(f"source.dtype: {source.dtype}")
        source_y_shape = self.rgba.shape[0]
        source_x_shape = self.rgba.shape[1]
        # source_y_shape = self._mandel.shape.y
        # source = 100 + np.random.randint(10, size=(source_x_shape, source_y_shape))

        # boolean 2-D array
        mapped = (frame_x >= 0.0) & (frame_x < source_x_shape) & (frame_y >= 0.0) & (frame_y < source_y_shape)

        # the target: frame array with source iteration values. Zero currently for invisible
        # result = np.zeros(shape=(self.y_shape, self.x_shape), dtype=np.float32)
        result = np.zeros(shape=(self.y_shape, self.x_shape, 4), dtype=np.uint8)

        # result = np.zeros(shape=frame_x.shape, dtype=int)

        # if frame is mapped
        # result[:, :] = source[frame_x[:,:], frame_y[:,:]]
        print(f"result.shape {result.shape}")
        print(f"source.shape {source.shape}")
        print(f"mapped.shape {mapped.shape}")

        result[mapped, :] = source[frame_y[mapped], frame_x[mapped], :]
        # result[~mapped] = np.nan

        timer_str = f"pan3\tborder: {self._mandel.has_border}"
        self._timer.start()
        self._ax_image2.remove()
        self._ax_image2: image.AxesImage = self._ax.imshow(
            result,
            interpolation='none', origin='lower', resample=False)
        # self._ax_image: image.AxesImage = self._ax.imshow(
        #     result,
        #     interpolation='none', origin='lower',
        #     cmap=self._cmap, vmin=0, vmax=100, alpha=1.0, zorder=0)
        self.figure_canvas.draw()
        self._timer.stop(name=timer_str, show=True)

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
        s, (width, height) = self._figure_canvas.print_to_buffer()
        graph_rgba: np.ndarray = np.frombuffer(s, np.uint8).reshape((height, width, 4))
        print(f"border: {self._mandel.has_border}\t, shape: {graph_rgba.shape}")

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

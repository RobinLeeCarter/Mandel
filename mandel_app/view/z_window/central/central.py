from typing import Optional

from PyQt5 import QtWidgets, QtCore, QtGui

from mandel_app import tuples
from mandel_app.model import z_model
from mandel_app.view.z_window.central import canvas


class Central:
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        # common of central area
        self._q_main_window: QtWidgets.QMainWindow = q_main_window
        self._q_scroll_area: XScrollArea = XScrollArea(self._q_main_window)
        self._q_main = QtWidgets.QWidget()
        self._q_main_layout = QtWidgets.QVBoxLayout(self._q_main)
        self.canvas: canvas.Canvas = canvas.Canvas()
        self.frame_shape: Optional[tuples.ImageShape] = None

    def build(self, image_shape: tuples.ImageShape):
        self.frame_shape = image_shape
        # make connections between common
        self._q_main_window.setCentralWidget(self._q_scroll_area)
        self._q_scroll_area.setWidget(self._q_main)
        self._q_main.setLayout(self._q_main_layout)
        self._q_main_layout.addWidget(self.canvas.figure_canvas, 1)

        # set properties of common
        self._q_scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self._q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._q_scroll_area.setStyleSheet("border: 0")
        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # self.q_main_layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.BottomToTop, self.q_main)
        self._q_main_layout.setSpacing(0)
        self._q_main_layout.setContentsMargins(0, 0, 0, 0)
        self.canvas.build(self.frame_shape)

        # self.q_main_layout.setAlignment(Qt.AlignBottom)
        # self.q_layout.setAlignment(self.canvas.mandel_canvas, QtCore.Qt.AlignCenter)
        # self.q_scroll_area.setAlignment(Qt.AlignBottom)
        # self.q_scroll_area.setWidget(self.canvas.mandel_canvas)
        # q_main_window.setCentralWidget(self.q_main)
        # self.q_main.setVisible(False) #  changed

        # getting _determine_image_space at this point in code gives a false reading as no image yet

    def show_graph(self, z_model_: z_model.ZModel):
        self.canvas.draw_graph(z_model_)
        self._q_main.setVisible(True)
        self._q_main.resize(self.frame_shape.x, self.frame_shape.y)  # changed
        self._q_main_layout.update()

    def hide_graph(self):
        self.canvas.clear_graph()

    def refresh_image_space(self):
        self.frame_shape = self._determine_image_space()

    def _determine_image_space(self) -> tuples.ImageShape:
        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        x = self._q_scroll_area.viewport().width()
        y = self._q_scroll_area.viewport().height()

        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        return tuples.ImageShape(x, y)


# This disables the scroll-wheel since we are using it for zooming
# plus the scrollbars are disabled
# removing the QScrollArea altogether messed up the image rendering and it was so hard to get right the first time
class XScrollArea(QtWidgets.QScrollArea):
    def wheelEvent(self, wheel_event: QtGui.QWheelEvent) -> None:
        wheel_event.ignore()

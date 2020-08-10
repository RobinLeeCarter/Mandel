from typing import Optional, Callable

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

import utils
from mandel_app import tuples
from mandel_app.model import mandelbrot
from mandel_app.view.central import mandel_image


class Central:
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        # scroll_area as central widget for main_window
        # self.q_main_window = q_main_window

        self.q_scroll_area = XScrollArea(q_main_window)
        self.q_scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.q_scroll_area.setStyleSheet("border: 0")
        self.image_space: Optional[tuples.ImageShape] = None

        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.q_main = QtWidgets.QWidget()
        # self.q_main = QtWidgets.QWidget(q_main_window)
        # self.q_main_layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.BottomToTop, self.q_main)
        self.q_main_layout = QtWidgets.QVBoxLayout(self.q_main)

        # self.layout = QtWidgets.QStackedLayout(self.main)
        self.q_main_layout.setSpacing(0)
        self.q_main_layout.setContentsMargins(0, 0, 0, 0)

        self.q_main.setLayout(self.q_main_layout)

        self.mandel_image = mandel_image.MandelImage()

        self.q_main_layout.addWidget(self.mandel_image.mandel_canvas)
        # self.q_main_layout.setAlignment(Qt.AlignBottom)

        # self.layout.setAlignment(self.mandel_image.mandel_canvas, QtCore.Qt.AlignCenter)

        self.q_scroll_area.setWidget(self.q_main)

        # self.q_scroll_area.setAlignment(Qt.AlignBottom)
        # self.q_scroll_area.setWidget(self.mandel_image.mandel_canvas)

        # q_main_window.setCentralWidget(self.q_main)
        q_main_window.setCentralWidget(self.q_scroll_area)
        self.q_main.setVisible(False)
        # getting image shape at this point gives a false reading

    def show_mandel(self, mandel: mandelbrot.Mandel):
        self.mandel_image.draw_mandel(mandel)
        # self.mandel_image.draw_mandel_test(mandel)
        self.q_main.setVisible(True)
        self.q_main.resize(mandel.shape.x, mandel.shape.y)
        self.q_main_layout.update()

    def set_image_space(self):
        self.image_space = self._get_image_space()

    def _get_image_space(self) -> tuples.ImageShape:
        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        x = self.q_scroll_area.viewport().width()
        y = self.q_scroll_area.viewport().height()

        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        return tuples.ImageShape(x, y)

    def set_on_resize(self, on_resize: Callable[[QtGui.QResizeEvent], None]):
        @QtCore.pyqtSlot()
        def slot(resize_event: QtGui.QResizeEvent):
            on_resize(resize_event)

        # noinspection PyUnresolvedReferences
        self.q_scroll_area.resizeEventSignal.connect(slot)


# This disables the scroll-wheel since we are using it for zooming
# plus the scrollbars are disabled
# removing the QScrollArea altogether messed up the image rendering and it was so hard to get right the first time
class XScrollArea(QtWidgets.QScrollArea):
    resizeEventSignal = QtCore.pyqtSignal(QtGui.QResizeEvent)

    def wheelEvent(self, wheel_event: QtGui.QWheelEvent) -> None:
        wheel_event.ignore()

    def resizeEvent(self, resize_event: QtGui.QResizeEvent) -> None:
        # noinspection PyUnresolvedReferences
        self.resizeEventSignal.emit(resize_event)
        super().resizeEvent(resize_event)

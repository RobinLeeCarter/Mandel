from typing import Optional

from PyQt5 import QtWidgets, QtCore

from mandel_app import tuples
from mandel_app.model import mandelbrot
from mandel_app.view import widgets
from mandel_app.view.window.central import canvas, overlay


class Central:
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        # scroll_area as central widget for main_window
        # self.q_main_window = q_main_window

        self._q_scroll_area: widgets.XScrollArea = widgets.XScrollArea(q_main_window)
        self._q_scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self._q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._q_scroll_area.setStyleSheet("border: 0")
        self.image_space: Optional[tuples.ImageShape] = None

        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self._q_main = QtWidgets.QWidget()
        # self.q_main = QtWidgets.QWidget(q_main_window)
        # self.q_main_layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.BottomToTop, self.q_main)
        self._q_main_layout = QtWidgets.QVBoxLayout(self._q_main)

        # self.q_layout = QtWidgets.QStackedLayout(self.main)
        self._q_main_layout.setSpacing(0)
        self._q_main_layout.setContentsMargins(0, 0, 0, 0)

        self._q_main.setLayout(self._q_main_layout)

        self.canvas: canvas.Canvas = canvas.Canvas()
        q_figure_canvas: widgets.XFigureCanvasQTAgg = self.canvas.figure_canvas
        self.overlay = overlay.Overlay(parent=q_figure_canvas)
        q_figure_canvas.set_overlay(self.overlay)

        self._q_main_layout.addWidget(q_figure_canvas)
        # self.q_main_layout.setAlignment(Qt.AlignBottom)

        # self.q_layout.setAlignment(self.canvas.mandel_canvas, QtCore.Qt.AlignCenter)

        self._q_scroll_area.setWidget(self._q_main)

        # self.q_scroll_area.setAlignment(Qt.AlignBottom)
        # self.q_scroll_area.setWidget(self.canvas.mandel_canvas)

        # q_main_window.setCentralWidget(self.q_main)
        q_main_window.setCentralWidget(self._q_scroll_area)
        self._q_main.setVisible(False)
        # getting image shape at this point gives a false reading

    def show_mandel(self, mandel: mandelbrot.Mandel):
        self.canvas.draw_mandel(mandel)
        # self.canvas.draw_mandel_test(mandel)
        self._q_main.setVisible(True)
        self._q_main.resize(mandel.shape.x, mandel.shape.y)
        self._q_main_layout.update()

    def refresh_image_space(self):
        self.image_space = self._determine_image_space()

    def _determine_image_space(self) -> tuples.ImageShape:
        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        x = self._q_scroll_area.viewport().width()
        y = self._q_scroll_area.viewport().height()

        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        return tuples.ImageShape(x, y)

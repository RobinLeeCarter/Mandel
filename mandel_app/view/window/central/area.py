from __future__ import annotations

from typing import Optional

from PyQt5 import QtWidgets, QtCore

from mandel_app import tuples
from mandel_app.view import widgets


class Area:
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        # scroll_area as central widget for main_window
        # self.q_main_window = q_main_window

        self._q_scroll_area: widgets.XScrollArea = widgets.XScrollArea(q_main_window)
        q_main_window.setCentralWidget(self._q_scroll_area)
        self.image_shape: Optional[tuples.ImageShape] = None
        self._q_main = QtWidgets.QWidget()
        self._q_main_layout = QtWidgets.QVBoxLayout(self._q_main)
        self._portal_label = widgets.XLabel(self._q_main)
        self._portal_label.setMouseTracking(True)
        # self.canvas: canvas.Canvas = canvas.Canvas()
        # q_figure_canvas: widgets.XFigureCanvasQTAgg = self.canvas.figure_canvas

        # TODO: Connect overlay
        # self.overlay = overlay.Overlay(parent=q_figure_canvas)
        # q_figure_canvas.set_overlay(self.overlay)

        # self._q_main_layout.addWidget(q_figure_canvas)
        # self.q_main_layout.setAlignment(Qt.AlignBottom)

        # self.q_layout.setAlignment(self.canvas.mandel_canvas, QtCore.Qt.AlignCenter)

        # TODO: Move to top
        # self._q_scroll_area.setWidget(self._q_main)

        # self.q_scroll_area.setAlignment(Qt.AlignBottom)
        # self.q_scroll_area.setWidget(self.canvas.mandel_canvas)

        # q_main_window.setCentralWidget(self.q_main)

        # getting image shape at this point gives a false reading

    def build(self):
        self._q_scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self._q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._q_scroll_area.setStyleSheet("border: 0")
        self._q_scroll_area.setWidget(self._q_main)
        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self._q_main.setVisible(False)
        self._q_main.setLayout(self._q_main_layout)

        self._q_main_layout.setSpacing(0)
        self._q_main_layout.setContentsMargins(0, 0, 0, 0)
        self._q_main_layout.addWidget(self._portal_label)

    @property
    def portal_label(self) -> widgets.XLabel:
        return self._portal_label

    def refresh(self):  # TODO: check removal ok , mandel: mandelbrot.Mandel
        # self.canvas.draw_mandel_test(mandel)
        self._q_main.setVisible(True)
        # self._q_main.resize(mandel.shape.x, mandel.shape.y)   TODO: check removal ok
        self._q_main_layout.update()

    def refresh_image_space(self):
        self.image_shape = self._determine_image_space()

    def _determine_image_space(self) -> tuples.ImageShape:
        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        x = self._q_scroll_area.viewport().width()
        y = self._q_scroll_area.viewport().height()

        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        return tuples.ImageShape(x, y)

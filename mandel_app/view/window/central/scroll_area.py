from __future__ import annotations

from typing import Optional

from PyQt5 import QtWidgets, QtCore

from mandel_app import tuples
from mandel_app.view import widgets


class ScrollArea:
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        """scroll bars mean that we can't get the size from the label"""
        self.shape: Optional[tuples.ImageShape] = None
        self._q_scroll_area: widgets.XScrollArea = widgets.XScrollArea(q_main_window)
        q_main_window.setCentralWidget(self._q_scroll_area)
        self._q_area_layout = QtWidgets.QVBoxLayout(self._q_scroll_area)
        self._portal_label = widgets.XLabel(self._q_scroll_area)

        self.build()
        # Getting image shape at this point, before window.show(), gives a false reading.

    def build(self):
        self._q_scroll_area.setLayout(self._q_area_layout)
        self._q_area_layout.addWidget(self._portal_label, stretch=1)

        self._q_scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self._q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._q_scroll_area.setStyleSheet("border: 0")
        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self._portal_label.setAlignment(QtCore.Qt.AlignCenter)
        # self._portal_label.setVisible(False)

        self._q_area_layout.setSpacing(0)
        self._q_area_layout.setContentsMargins(0, 0, 0, 0)

        self._portal_label.setMouseTracking(True)

    @property
    def portal_label(self) -> widgets.XLabel:
        return self._portal_label

    def get_shape(self) -> tuples.ImageShape:
        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        x = self._q_scroll_area.viewport().width()
        y = self._q_scroll_area.viewport().height()

        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        return tuples.ImageShape(x, y)

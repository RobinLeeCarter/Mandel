from typing import Callable

from PyQt5 import QtGui, QtWidgets, QtCore

import utils
_ICON_PATH = r"resources/icons/"


class Image:
    def __init__(self, icon_filename: str):
        self.q_pixmap = QtGui.QPixmap(utils.full_path(_ICON_PATH + icon_filename))
        self.q_label = XLabel()
        self.q_label.setPixmap(self.q_pixmap)

    def set_on_mouse_press(self, on_mouse_press: Callable[[QtGui.QMouseEvent], None]):
        @QtCore.pyqtSlot()
        def slot(mouse_event: QtGui.QMouseEvent):
            on_mouse_press(mouse_event)

        # noinspection PyUnresolvedReferences
        self.q_label.mousePressSignal.connect(slot)


class XLabel(QtWidgets.QLabel):
    mousePressSignal = QtCore.pyqtSignal(QtGui.QMouseEvent)

    def mousePressEvent(self, mouse_event: QtGui.QMouseEvent):
        # noinspection PyUnresolvedReferences
        self.mousePressSignal.emit(mouse_event)
        super().mousePressEvent(mouse_event)

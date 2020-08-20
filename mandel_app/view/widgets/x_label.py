from typing import Callable

from PyQt5 import QtGui, QtWidgets, QtCore


class XLabel(QtWidgets.QLabel):
    mousePressSignal = QtCore.pyqtSignal(QtGui.QMouseEvent)

    def mousePressEvent(self, mouse_event: QtGui.QMouseEvent):
        self.mousePressSignal.emit(mouse_event)
        super().mousePressEvent(mouse_event)

    def set_on_mouse_press(self, on_mouse_press: Callable[[QtGui.QMouseEvent], None]):
        self.mousePressSignal.connect(on_mouse_press)

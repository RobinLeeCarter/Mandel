from typing import Callable, Optional

from PyQt5 import QtGui, QtWidgets, QtCore

from mandel_app.view import common


class XLabel(QtWidgets.QLabel):
    mousePressSignal = QtCore.pyqtSignal(QtGui.QMouseEvent)
    mouseReleaseSignal = QtCore.pyqtSignal(QtGui.QMouseEvent)
    mouseMoveSignal = QtCore.pyqtSignal(QtGui.QMouseEvent)
    wheelSignal = QtCore.pyqtSignal(QtGui.QWheelEvent)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._overlay: Optional[common.BaseOverlay] = None

    def paintEvent(self, q_paint_event: QtGui.QPaintEvent):
        super().paintEvent(q_paint_event)
        self._overlay.draw(q_paint_event)

    def set_overlay(self, overlay_: common.BaseOverlay):
        self._overlay = overlay_

    def mousePressEvent(self, mouse_event: QtGui.QMouseEvent):
        mouse_event.accept()
        self.mousePressSignal.emit(mouse_event)
        # super().mousePressEvent(mouse_event)

    def set_on_mouse_press(self, on_mouse_press: Callable[[QtGui.QMouseEvent], None]):
        self.mousePressSignal.connect(on_mouse_press)

    def mouseReleaseEvent(self, mouse_event: QtGui.QMouseEvent):
        mouse_event.accept()
        self.mouseReleaseSignal.emit(mouse_event)
        # super().mouseReleaseEvent(mouse_event)

    def set_on_mouse_release(self, on_mouse_release: Callable[[QtGui.QMouseEvent], None]):
        self.mousePressSignal.connect(on_mouse_release)

    def mouseMoveEvent(self, mouse_event: QtGui.QMouseEvent):
        mouse_event.accept()
        self.mouseMoveSignal.emit(mouse_event)
        # super().mouseMoveEvent(mouse_event)

    def set_on_mouse_move(self, on_mouse_move: Callable[[QtGui.QMouseEvent], None]):
        self.mousePressSignal.connect(on_mouse_move)

    def wheelEvent(self, wheel_event: QtGui.QWheelEvent):
        wheel_event.accept()
        self.wheelSignal.emit(wheel_event)
        # super().mouseMoveEvent(mouse_event)

    def set_on_wheel(self, on_wheel: Callable[[QtGui.QWheelEvent], None]):
        self.mousePressSignal.connect(on_wheel)

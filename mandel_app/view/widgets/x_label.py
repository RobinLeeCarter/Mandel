from typing import Callable, Optional

from PyQt5 import QtGui, QtWidgets, QtCore

from mandel_app.view.common import base_overlay


class XLabel(QtWidgets.QLabel):
    # region Setup
    mousePressSignal = QtCore.pyqtSignal(QtGui.QMouseEvent)
    mouseMoveSignal = QtCore.pyqtSignal(QtGui.QMouseEvent)
    mouseReleaseSignal = QtCore.pyqtSignal(QtGui.QMouseEvent)
    mouseDoubleClickSignal = QtCore.pyqtSignal(QtGui.QMouseEvent)
    wheelSignal = QtCore.pyqtSignal(QtGui.QWheelEvent)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_cursor_shape: Optional[QtCore.Qt.CursorShape] = None
        self._overlay: Optional[base_overlay.BaseOverlay] = None

    def set_overlay(self, overlay_: base_overlay.BaseOverlay):
        self._overlay = overlay_

    def set_cursor_shape(self, new_cursor_shape: QtCore.Qt.CursorShape):
        if self._current_cursor_shape is None or self._current_cursor_shape != new_cursor_shape:
            new_cursor = QtGui.QCursor(new_cursor_shape)
            self.setCursor(new_cursor)
            self._current_cursor_shape = new_cursor_shape
    # endregion

    # region Overridden Events
    def paintEvent(self, q_paint_event: QtGui.QPaintEvent):
        super().paintEvent(q_paint_event)
        if self._overlay is not None:
            self._overlay.draw(q_paint_event)

    def mousePressEvent(self, mouse_event: QtGui.QMouseEvent):
        mouse_event.accept()
        self.mousePressSignal.emit(mouse_event)
        # super().mousePressEvent(mouse_event)

    def mouseMoveEvent(self, mouse_event: QtGui.QMouseEvent):
        mouse_event.accept()
        self.mouseMoveSignal.emit(mouse_event)
        # super().mouseMoveEvent(mouse_event)

    def mouseReleaseEvent(self, mouse_event: QtGui.QMouseEvent):
        mouse_event.accept()
        self.mouseReleaseSignal.emit(mouse_event)
        # super().mouseReleaseEvent(mouse_event)

    def mouseDoubleClickEvent(self, mouse_event: QtGui.QMouseEvent):
        mouse_event.accept()
        self.mouseDoubleClickSignal.emit(mouse_event)
        # super().mouseDoubleClickEvent(mouse_event)

    def wheelEvent(self, wheel_event: QtGui.QWheelEvent):
        wheel_event.accept()
        self.wheelSignal.emit(wheel_event)
        # super().wheelEvent(mouse_event)
    # endregion

    # region Connect Events
    def set_on_mouse_press(self, on_mouse_press: Callable[[QtGui.QMouseEvent], None]):
        self.mousePressSignal.connect(on_mouse_press)

    def set_on_mouse_move(self, on_mouse_move: Callable[[QtGui.QMouseEvent], None]):
        self.mouseMoveSignal.connect(on_mouse_move)

    def set_on_mouse_release(self, on_mouse_release: Callable[[QtGui.QMouseEvent], None]):
        self.mouseReleaseSignal.connect(on_mouse_release)

    def set_on_mouse_double_click(self, on_mouse_double_click: Callable[[QtGui.QMouseEvent], None]):
        self.mouseDoubleClickSignal.connect(on_mouse_double_click)

    def set_on_wheel(self, on_wheel: Callable[[QtGui.QWheelEvent], None]):
        self.wheelSignal.connect(on_wheel)
    # endregion

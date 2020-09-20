from PyQt5 import QtGui, QtWidgets

from mandel_app.view import common
from mandel_app.view.window.central.overlay import copy_message


class Overlay(common.BaseOverlay):
    def __init__(self, parent: QtWidgets.QWidget):
        # parent is the q_object we are overlaying
        super().__init__(parent)
        self._copy_message: copy_message.CopyMessage = copy_message.CopyMessage(
            parent=self._parent,
            hide_callback=self.hide_copy_message
        )
        self._refresh_overlay_visible()

    def show_copy_message(self):
        self._copy_message.visible = True
        self._refresh_overlay_visible()
        self._parent.update()
        self._copy_message.start_hide_timer()

    def hide_copy_message(self):
        self._copy_message.visible = False
        self._refresh_overlay_visible()
        self._parent.update()

    def _refresh_overlay_visible(self):
        if self._copy_message.visible:
            self.visible = True
        else:
            self.visible = False

    def _paint(self, q_paint_event: QtGui.QPaintEvent):
        q_painter = QtGui.QPainter()
        q_painter.begin(self._parent)
        self._copy_message.draw(q_painter, q_paint_event)
        q_painter.end()

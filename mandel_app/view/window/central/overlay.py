from PyQt5 import QtGui, QtWidgets

from mandel_app.view.window.central import copy_message


class Overlay:
    def __init__(self, parent: QtWidgets.QWidget):
        # parent is the q_object we are overlaying
        self.parent = parent
        self.visible: bool = False
        self._copy_message = copy_message.CopyMessage(parent=self.parent, hide_callback=self.hide_copy_message)
        self._refresh_overlay_visible()

    def _refresh_overlay_visible(self):
        if self._copy_message.visible:
            self.visible = True
        else:
            self.visible = False

    def show_copy_message(self):
        self._copy_message.visible = True
        self._refresh_overlay_visible()
        self.parent.draw()
        self._copy_message.start_hide_timer()

    def hide_copy_message(self):
        self._copy_message.visible = False
        self._refresh_overlay_visible()
        self.parent.draw()

    def draw(self, q_paint_event: QtGui.QPaintEvent):
        if self.visible:
            q_painter = QtGui.QPainter()
            q_painter.begin(self.parent)
            self._copy_message.draw(q_painter, q_paint_event)
            q_painter.end()

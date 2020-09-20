from abc import ABC, abstractmethod
from PyQt5 import QtGui, QtWidgets


class BaseOverlay(ABC):
    def __init__(self, parent: QtWidgets.QWidget):
        # parent is the q_object we are overlaying
        self._parent: QtWidgets.QWidget = parent
        self.visible: bool = False

    def draw(self, q_paint_event: QtGui.QPaintEvent):
        if self.visible:
            self._paint(q_paint_event)

    @abstractmethod
    def _paint(self, q_paint_event: QtGui.QPaintEvent):
        pass

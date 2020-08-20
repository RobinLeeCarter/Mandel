from __future__ import annotations
from typing import Optional

from matplotlib.backends import backend_qt5agg

from PyQt5 import QtGui
from mandel_app.view.window.central import overlay


class XFigureCanvasQTAgg(backend_qt5agg.FigureCanvasQTAgg):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._overlay: Optional[overlay.Overlay] = None

    def set_overlay(self, overlay_: overlay.Overlay):
        self._overlay = overlay_

    def paintEvent(self, q_paint_event: QtGui.QPaintEvent):
        super().paintEvent(q_paint_event)
        self._overlay.draw(q_paint_event)

from typing import Optional, Callable

from PyQt5 import QtGui, QtCore


class CopyMessage:
    MESSAGE_TIMEOUT_MS: int = 2000

    def __init__(self, parent: QtCore.QObject, hide_callback: Callable[[], None]):
        self._hide_q_timer = QtCore.QTimer(parent)
        self._hide_q_timer.setSingleShot(True)
        self._hide_q_timer.timeout.connect(hide_callback)
        # self._hide_q_timer.timeout.connect(hide_callback)

        self.visible: bool = False
        self._alpha_f: float = 0.8

        self._q_painter: Optional[QtGui.QPainter] = None
        self._window_rect: Optional[QtCore.QRect] = None

    def draw(self, q_painter: QtGui.QPainter, q_paint_event: QtGui.QPaintEvent):
        if self.visible:
            self._q_painter = q_painter
            q_painter.setRenderHint(QtGui.QPainter.Antialiasing)
            self._window_rect = q_paint_event.rect()
            self._build()

    def _build(self):
        q_painter = self._q_painter

        rect_center = QtCore.QPoint(
            self._window_rect.center().x(),
            self._window_rect.height() - 50
        )
        rect_size = QtCore.QSizeF(200.0, 22.0)
        rect_left_top_point = QtCore.QPointF(
            rect_center.x()-round(rect_size.width()*0.5-0.5),
            rect_center.y()-round(rect_size.height()*0.5-0.5)
        )
        q_rect_f = QtCore.QRectF(rect_left_top_point, rect_size)

        self._build_rounded_rect(q_rect_f)

        # _q_painter.setPen(QtGui.QColor(53, 84, 218))
        q_text_color = QtGui.QColor(QtCore.Qt.black)
        # q_text_color.setAlphaF(self._alpha_f)
        q_painter.setPen(q_text_color)
        q_painter.setFont(QtGui.QFont('Decorative', 12))
        q_painter.drawText(q_rect_f, QtCore.Qt.AlignCenter, "statistics copied")

    def _build_rounded_rect(self, q_rect_f: QtCore.QRectF):
        q_painter = self._q_painter

        q_edge_color = QtGui.QColor(QtCore.Qt.black)
        q_edge_color.setAlphaF(self._alpha_f)

        q_fill_color = QtGui.QColor(QtCore.Qt.lightGray)
        q_fill_color.setAlphaF(self._alpha_f)

        q_painter.setPen(q_edge_color)
        q_painter_path = QtGui.QPainterPath()
        q_painter_path.addRoundedRect(q_rect_f, 10.0, 10.0)
        q_painter.fillPath(q_painter_path, q_fill_color)
        q_painter.drawPath(q_painter_path)  # seemingly unnecessary

    def start_hide_timer(self):
        self._hide_q_timer.start(CopyMessage.MESSAGE_TIMEOUT_MS)

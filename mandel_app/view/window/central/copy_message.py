from PyQt5 import QtGui, QtCore


class CopyMessage:
    def __init__(self, q_painter, event: QtGui.QPaintEvent):
        self.q_painter = q_painter
        q_painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.alpha_f = 0.8
        self.window_rect = event.rect()
        self._build()

    def _build(self):
        q_painter = self.q_painter

        rect_center = QtCore.QPoint(
            self.window_rect.center().x(),
            self.window_rect.height() - 50
        )
        rect_size = QtCore.QSizeF(200.0, 22.0)
        rect_left_top_point = QtCore.QPointF(
            rect_center.x()-round(rect_size.width()*0.5-0.5),
            rect_center.y()-round(rect_size.height()*0.5-0.5)
        )
        q_rect_f = QtCore.QRectF(rect_left_top_point, rect_size)

        self._build_rounded_rect(q_rect_f)

        # q_painter.setPen(QtGui.QColor(53, 84, 218))
        q_text_color = QtGui.QColor(QtCore.Qt.black)
        # q_text_color.setAlphaF(self.alpha_f)
        q_painter.setPen(q_text_color)
        q_painter.setFont(QtGui.QFont('Decorative', 12))
        q_painter.drawText(q_rect_f, QtCore.Qt.AlignCenter, "statistics copied")

    def _build_rounded_rect(self, q_rect_f: QtCore.QRectF):
        q_painter = self.q_painter

        q_edge_color = QtGui.QColor(QtCore.Qt.black)
        q_edge_color.setAlphaF(self.alpha_f)

        q_fill_color = QtGui.QColor(QtCore.Qt.lightGray)
        q_fill_color.setAlphaF(self.alpha_f)

        q_painter.setPen(q_edge_color)
        q_painter_path = QtGui.QPainterPath()
        q_painter_path.addRoundedRect(q_rect_f, 10.0, 10.0)
        q_painter.fillPath(q_painter_path, q_fill_color)
        q_painter.drawPath(q_painter_path)  # seemingly unnecessary

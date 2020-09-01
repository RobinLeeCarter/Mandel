# From Stack-overflow. Jason's solution.
# https://stackoverflow.com/questions/47494305/python-pyqt4-slider-with-tick-labels

import sys
from typing import Callable

from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QStyle, QStyleOptionSlider
from PyQt5.QtCore import QRect, QPoint, Qt


class XLabeledSlider(QtWidgets.QWidget):
    def __init__(self, minimum, maximum, interval=1, orientation=Qt.Horizontal, labels=None, parent=None):
        super().__init__(parent=parent)

        _levels = range(minimum, maximum + interval, interval)
        if labels is not None:
            if not isinstance(labels, (tuple, list)):
                raise Exception("<labels> is a list or tuple.")
            if len(labels) != len(_levels):
                raise Exception("Size of <labels> doesn't match levels.")
            self.levels = list(zip(_levels, labels))
        else:
            self.levels = list(zip(_levels, map(str, _levels)))

        if orientation == Qt.Horizontal:
            self._layout = QtWidgets.QVBoxLayout(self)
        elif orientation == Qt.Vertical:
            self._layout = QtWidgets.QHBoxLayout(self)
        else:
            raise Exception("<orientation> wrong.")

        # gives some space to print labels
        self._left_margin = 10
        self._top_margin = 0
        self._right_margin = 10
        self._bottom_margin = 10

        self._layout.setContentsMargins(self._left_margin, self._top_margin,
                                        self._right_margin, self._bottom_margin)

        self.q_slider = QtWidgets.QSlider(orientation, self)
        self.q_slider.setMinimum(minimum)
        self.q_slider.setMaximum(maximum)
        self.q_slider.setValue(minimum)
        if orientation == Qt.Horizontal:
            self.q_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
            self.q_slider.setMinimumWidth(100)  # just to make it easier to read
        else:
            self.q_slider.setTickPosition(QtWidgets.QSlider.TicksLeft)
            self.q_slider.setMinimumHeight(100)  # just to make it easier to read
        self.q_slider.setTickInterval(interval)
        self.q_slider.setSingleStep(1)

        self._layout.addWidget(self.q_slider)

    def paintEvent(self, e):
        super().paintEvent(e)

        style = self.q_slider.style()
        painter = QPainter(self)
        st_slider = QStyleOptionSlider()
        st_slider.initFrom(self.q_slider)
        st_slider.orientation = self.q_slider.orientation()

        length = style.pixelMetric(QStyle.PM_SliderLength, st_slider, self.q_slider)
        available = style.pixelMetric(QStyle.PM_SliderSpaceAvailable, st_slider, self.q_slider)

        for v, v_str in self.levels:

            # get the size of the label
            rect = painter.drawText(QRect(), Qt.TextDontPrint, v_str)

            if self.q_slider.orientation() == Qt.Horizontal:
                # I assume the offset is half the length of slider, therefore
                # + length//2
                x_loc = QStyle.sliderPositionFromValue(self.q_slider.minimum(),
                                                       self.q_slider.maximum(), v, available) + length // 2

                # left bound of the text = center - half of text width + L_margin
                left = x_loc - rect.width() // 2 + self._left_margin
                bottom = self.rect().bottom()

                # enlarge margins if clipping
                if v == self.q_slider.minimum():
                    if left <= 0:
                        self._left_margin = rect.width() // 2 - x_loc
                    if self._bottom_margin <= rect.height():
                        self._bottom_margin = rect.height()

                    self._layout.setContentsMargins(self._left_margin,
                                                    self._top_margin, self._right_margin,
                                                    self._bottom_margin)

                if v == self.q_slider.maximum() and rect.width() // 2 >= self._right_margin:
                    self._right_margin = rect.width() // 2
                    self._layout.setContentsMargins(self._left_margin,
                                                    self._top_margin, self._right_margin,
                                                    self._bottom_margin)

            else:
                y_loc = QStyle.sliderPositionFromValue(self.q_slider.minimum(),
                                                       self.q_slider.maximum(), v, available, upsideDown=True)

                bottom = y_loc + length // 2 + rect.height() // 2 + self._top_margin - 3
                # there is a 3 px offset that I can't attribute to any metric

                left = self._left_margin - rect.width()
                if left <= 0:
                    self._left_margin = rect.width() + 2
                    self._layout.setContentsMargins(self._left_margin,
                                                    self._top_margin, self._right_margin,
                                                    self._bottom_margin)

            pos = QPoint(left, bottom)
            painter.drawText(pos, v_str)

        return

    def set_on_slider_moved(self, on_slider_moved: Callable[[int], None]):
        # noinspection PyUnresolvedReferences
        self.q_slider.sliderMoved.connect(on_slider_moved)

    def set_on_value_changed(self, on_value_changed: Callable[[int], None]):
        # noinspection PyUnresolvedReferences
        self.q_slider.valueChanged.connect(on_value_changed)


# test script
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    q_widget = QtWidgets.QWidget()
    q_layout = QtWidgets.QHBoxLayout()
    q_widget.setLayout(q_layout)

    w = XLabeledSlider(1, 10, 1, orientation=Qt.Horizontal)

    q_layout.addWidget(w)
    q_widget.show()
    sys.exit(app.exec_())

from typing import Callable

from PyQt5 import QtWidgets


class Dial:
    def __init__(self, q_main_window: QtWidgets.QMainWindow, size: int):
        # dial for rotating the mandlebrot
        self.q_dial = QtWidgets.QDial(q_main_window)
        self.q_dial.setMinimum(0)
        self.q_dial.setMaximum(360)
        self.q_dial.setValue(180)
        self.q_dial.setWrapping(True)
        self.q_dial.setTracking(False)
        self.q_dial.setFixedWidth(size)

    @staticmethod
    def _convert_to_theta(value: int) -> int:
        return value - 180

    def set_on_rotating(self, on_rotating: Callable[[int], None]):
        def slot(value: int):
            theta_degrees = Dial._convert_to_theta(value)
            on_rotating(theta_degrees)

        # noinspection PyUnresolvedReferences
        self.q_dial.sliderMoved.connect(slot)

    def set_on_rotated(self, on_rotated: Callable[[int], None]):
        def slot(value: int):
            theta_degrees = Dial._convert_to_theta(value)
            on_rotated(theta_degrees)

        # noinspection PyUnresolvedReferences
        self.q_dial.valueChanged.connect(slot)

    def set_value(self, theta_degrees: int):
        value = theta_degrees - 180
        self.q_dial.blockSignals(True)
        self.q_dial.setValue(value)
        self.q_dial.blockSignals(False)

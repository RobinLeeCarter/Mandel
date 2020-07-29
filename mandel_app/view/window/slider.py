from typing import Callable

from PyQt5 import QtWidgets, QtCore

from mandel_app.view.window import labelled_slider


class Slider:
    def __init__(self, q_main_window: QtWidgets.QMainWindow):

        self.labelled_slider = labelled_slider.LabeledSlider(
            minimum=17,
            maximum=30,
            parent=q_main_window
        )
        self.q_slider = self.labelled_slider.q_slider
        self.q_slider.setTracking(False)
        self.labelled_slider.setFixedWidth(300)

        # self.q_slider.setValue(20)
        # slider for setting maximum iterations
        # self.q_slider = QtWidgets.QSlider(orientation=QtCore.Qt.Horizontal, parent=q_main_window)
        # self.q_slider.setFocusPolicy(QtCore.Qt.StrongFocus)
        # # self.q_slider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        # self.q_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        # self.q_slider.setMinimum(5)
        # self.q_slider.setMaximum(10)
        # self.q_slider.setValue(6)
        # self.q_slider.setTickInterval(1)
        # self.q_slider.setSingleStep(1)

    # def set_on_value_changed(self, on_value_changed: Callable[[int], None]):
    #     @QtCore.pyqtSlot()
    #     def slot(value: int):
    #         print(value)
    #         on_value_changed(value)
    #
    #     # noinspection PyUnresolvedReferences
    #     self.q_slider.valueChanged.connect(slot)

    # def __init__(self, q_main_window: QtWidgets.QMainWindow):
    #     # slider for setting maximum iterations
    #     self.q_slider = QtWidgets.QSlider(orientation=QtCore.Qt.Horizontal, parent=q_main_window)
    #     self.q_slider.setFocusPolicy(QtCore.Qt.StrongFocus)
    #     # self.q_slider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
    #     self.q_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
    #     self.q_slider.setMinimum(5)
    #     self.q_slider.setMaximum(10)
    #     self.q_slider.setValue(6)
    #     self.q_slider.setTickInterval(1)
    #     self.q_slider.setSingleStep(1)
    #     self.q_slider.setTracking(False)
    #     self.q_slider.setFixedWidth(100)


    #
    # def set_rotated_function(self, rotated_function: Callable[[int], None]):
    #     @QtCore.pyqtSlot()
    #     def slot(value: int):
    #         theta_degrees = value - 180
    #         rotated_function(theta_degrees)
    #
    #     # noinspection PyUnresolvedReferences
    #     self.q_dial.valueChanged.connect(slot)
    #
    # def set_value(self, theta_degrees: int):
    #     value = theta_degrees - 180
    #     self.q_dial.blockSignals(True)
    #     self.q_dial.setValue(value)
    #     self.q_dial.blockSignals(False)

from PyQt5 import QtWidgets

from mandel_app.view import widgets


class IterationSlider:
    def __init__(self, q_main_window: QtWidgets.QMainWindow):

        self.x_labelled_slider: widgets.XLabeledSlider = widgets.XLabeledSlider(
            minimum=17,
            maximum=30,
            parent=q_main_window
        )
        self.x_labelled_slider.setFixedWidth(300)
        self._q_slider = self.x_labelled_slider.q_slider
        self._q_slider.setTracking(False)

    @property
    def value(self) -> int:
        return self._q_slider.value()

    @value.setter
    def value(self, new_value: int):
        self._q_slider.setValue(new_value)

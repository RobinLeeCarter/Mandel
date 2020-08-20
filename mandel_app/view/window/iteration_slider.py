from typing import Callable

from PyQt5 import QtWidgets

from mandel_app.view import widgets


class IterationSlider:
    def __init__(self, q_main_window: QtWidgets.QMainWindow):

        self.q_labelled_slider: widgets.XLabeledSlider = widgets.XLabeledSlider(
            minimum=17,
            maximum=30,
            parent=q_main_window
        )
        self.q_labelled_slider.setFixedWidth(300)
        self._q_slider = self.q_labelled_slider.q_slider
        self._q_slider.setTracking(False)

    def set_on_slider_moved(self, on_slider_moved: Callable[[int], None]):
        self._q_slider.sliderMoved.connect(on_slider_moved)

    def set_on_value_changed(self, on_value_changed: Callable[[int], None]):
        self._q_slider.valueChanged.connect(on_value_changed)

    @property
    def value(self) -> int:
        return self._q_slider.value()

    @value.setter
    def value(self, new_value: int):
        self._q_slider.setValue(new_value)

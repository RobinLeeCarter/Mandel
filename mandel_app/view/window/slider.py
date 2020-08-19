from PyQt5 import QtWidgets

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

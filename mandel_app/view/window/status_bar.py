import math
from typing import Optional, Callable

from PyQt5 import QtWidgets, QtCore, QtGui

from mandel_app.view import image, x_label
from mandel_app.model.mandelbrot import mandel


class StatusBar:
    # region Setup
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        # status_bar for main_window
        self.q_status_bar = QtWidgets.QStatusBar(q_main_window)
        q_main_window.setStatusBar(self.q_status_bar)

        # q_layout widgets
        self._q_widget = QtWidgets.QWidget(self.q_status_bar)
        self.q_status_bar.addWidget(self._q_widget, 1)

        self._q_layout = QtWidgets.QHBoxLayout()
        self._q_layout.setSpacing(0)
        self._q_layout.setContentsMargins(0, 0, 0, 0)
        self._q_widget.setLayout(self._q_layout)

        # build up components
        self._q_left_label: x_label.XLabel = self._build_label()

        self._q_center_label: x_label.XLabel = self._build_label(align=QtCore.Qt.AlignCenter)
        self._copy_icon_image: image.Image = image.Image("document-copy.png")
        self._copy_icon_image.set_visible(False)
        self._q_center_widget: QtWidgets.QWidget = self._build_center_widget()

        self._q_right_label: x_label.XLabel = self._build_label(visible=False)
        self._q_progress_bar: QtWidgets.QProgressBar = self._build_progress_bar()
        self._q_right_widget: QtWidgets.QWidget = self._build_right_widget()

        self._q_layout.addWidget(self._q_left_label, stretch=1)
        self._q_layout.addWidget(self._q_center_widget, stretch=1)
        self._q_layout.addWidget(self._q_right_widget, stretch=1)

        self._zoom_digits: int = 0
        self._dp: int = 2
        self.verbose_mandel_statistics: str = ""

    def _build_label(self,
                     align: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignLeft,
                     visible: bool = True) -> x_label.XLabel:
        q_label = x_label.XLabel("")
        q_label.setAlignment(align)
        if not visible:
            q_label.setVisible(visible)
        return q_label

    def _build_center_widget(self) -> QtWidgets.QWidget:
        q_widget = QtWidgets.QWidget()
        q_layout = QtWidgets.QHBoxLayout()
        q_widget.setLayout(q_layout)

        q_layout.setSpacing(0)
        q_layout.setContentsMargins(0, 0, 0, 0)
        q_layout.addStretch()   # stretch will fill any empty space
        q_layout.addWidget(self._q_center_label)
        q_layout.addSpacing(5)
        q_layout.addWidget(self._copy_icon_image.q_label)
        q_layout.addStretch()

        # return q_right_label
        return q_widget

    def _build_right_widget(self) -> QtWidgets.QWidget:
        q_widget = QtWidgets.QWidget()
        q_layout = QtWidgets.QHBoxLayout()
        q_widget.setLayout(q_layout)
        q_layout.setSpacing(0)
        q_layout.setContentsMargins(0, 0, 0, 0)
        q_layout.addStretch()   # stretch will fill any empty space
        q_layout.addWidget(self._q_right_label)
        q_layout.addWidget(self._q_progress_bar)

        # return q_right_label
        return q_widget

    def _build_progress_bar(self) -> QtWidgets.QProgressBar:
        q_progress_bar = QtWidgets.QProgressBar()
        q_progress_bar.setAlignment(QtCore.Qt.AlignRight)
        q_progress_bar.setRange(0, 100)
        q_progress_bar.setMaximumHeight(15)
        q_progress_bar.setMaximumWidth(200)
        q_progress_bar.setTextVisible(True)
        q_progress_bar.setFormat("Calculating...")
        q_progress_bar.setVisible(False)
        return q_progress_bar
    # endregion

    # region display requests from View
    def set_center_on_mouse_press(self, on_mouse_press: Callable[[QtGui.QMouseEvent], None]):
        self._copy_icon_image.set_on_mouse_press(on_mouse_press)
        self._q_center_label.set_on_mouse_press(on_mouse_press)

    def display_progress(self, progress: float):
        # pass
        progress_int_percentage = round(100*progress)
        self._q_progress_bar.setValue(progress_int_percentage)
        self._q_right_label.setVisible(False)
        self._q_progress_bar.setVisible(True)

    def refresh_mandel_statistics(self, mandel_: mandel.Mandel):
        message = self._get_mandel_statistics(mandel_)
        self._q_center_label.setText(message)
        self._copy_icon_image.set_visible(True)
        self.verbose_mandel_statistics = self._get_mandel_statistics(mandel_, verbose=True)

    def display_time_taken(self, total_time):
        # pass
        if total_time != 0.0:
            message = f"Completed in {total_time:.2f} seconds"
        else:
            message = "Complete..."
        self._q_right_label.setText(message)
        self._q_progress_bar.setVisible(False)
        self._q_right_label.setVisible(True)

    def display_point(self, z: complex):
        message = "point: " + self._complex_to_display_text(z, self._dp)
        self._q_left_label.setText(message)

    def _get_mandel_statistics(self, mandel_: mandel.Mandel, verbose: bool = False) -> str:
        if verbose:
            message = "center: " + self._complex_to_display_text(mandel_.centre)
            message += f"  size: {mandel_.x_size}"
            message += f"  rotation: {mandel_.theta_degrees} degrees"
        else:
            self._zoom_digits: int = max(0, round(-math.log10(mandel_.x_size)))
            self._dp = self._zoom_digits + 2
            message = "center: " + self._complex_to_display_text(mandel_.centre, self._dp)
            message += f"  size: {mandel_.x_size:.3g}"
            message += f"  rotation: {mandel_.theta_degrees}" + u"\N{DEGREE SIGN}"
        return message

    @staticmethod
    def _complex_to_display_text(z: complex, dp: Optional[int] = None) -> str:
        if dp is None:
            text = f"{z.real}"
        else:
            text = f"{z.real:.{dp}f}"

        if z.imag >= 0.0:
            text += " +"
        else:
            text += " -"

        if dp is None:
            text += f"{abs(z.imag)}i"
        else:
            text += f"{abs(z.imag):.{dp}f}i"

        return text
    # endregion

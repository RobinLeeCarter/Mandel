from PyQt5 import QtWidgets, QtCore


class StatusBar:
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        # status_bar for main_window
        self.q_status_bar = QtWidgets.QStatusBar(q_main_window)
        q_main_window.setStatusBar(self.q_status_bar)

        # q_layout widgets
        self.q_widget = QtWidgets.QWidget(self.q_status_bar)
        self.q_status_bar.addWidget(self.q_widget, 1)
        self.q_layout = QtWidgets.QHBoxLayout()
        self.q_layout.setSpacing(0)
        self.q_layout.setContentsMargins(0, 0, 0, 0)
        self.q_widget.setLayout(self.q_layout)

        # "normal" label added to status_bar
        self.q_left_label = self.make_left_label()

        self.q_center_label = self.make_center_label()

        self.q_right_label = self.make_right_label()
        self.q_progress_bar = self.make_progress_bar()
        self.q_right_widget = self.make_right_widget()

        # self.q_layout.addWidget(self.q_left_label)
        # self.q_layout.addWidget(self.q_center_label)
        # self.q_layout.addWidget(self.q_right_widget)
        # self.q_layout.addWidget(self.q_progress_bar)

        self.q_layout.addWidget(self.q_left_label, stretch=1)
        self.q_layout.addWidget(self.q_center_label, stretch=1)
        self.q_layout.addWidget(self.q_right_widget, stretch=1)
        # self.q_layout.addWidget(self.q_progress_bar, stretch=1000)

        # self.q_status_bar.addWidget(self.q_left_label)
        # self.q_status_bar.addPermanentWidget(self.q_progress_bar)
        # self.q_status_bar.addWidget(self.q_center_label, 1)
        # self.q_status_bar.addPermanentWidget(self.q_center_label)

    def make_left_label(self) -> QtWidgets.QLabel:
        q_left_label = QtWidgets.QLabel("Left text")
        q_left_label.setAlignment(QtCore.Qt.AlignLeft)
        return q_left_label

    def make_center_label(self) -> QtWidgets.QLabel:
        q_center_label = QtWidgets.QLabel("Center text")
        q_center_label.setAlignment(QtCore.Qt.AlignCenter)
        return q_center_label

    def make_right_label(self) -> QtWidgets.QLabel:
        q_right_label = QtWidgets.QLabel("")
        # q_right_label.resize(1000, q_right_label.height())
        q_right_label.setMinimumWidth(200)
        q_right_label.setAlignment(QtCore.Qt.AlignCenter)
        q_right_label.setVisible(False)
        return q_right_label

    def make_right_widget(self) -> QtWidgets.QWidget:
        q_widget = QtWidgets.QWidget()
        q_layout = QtWidgets.QHBoxLayout()
        q_widget.setLayout(q_layout)
        q_layout.setSpacing(0)
        q_layout.setContentsMargins(0, 0, 0, 0)
        q_layout.addStretch()   # stretch will fill any empty space
        q_layout.addWidget(self.q_right_label)
        q_layout.addWidget(self.q_progress_bar)

        # return q_right_label
        return q_widget

    def make_progress_bar(self) -> QtWidgets.QProgressBar:
        q_progress_bar = QtWidgets.QProgressBar()
        q_progress_bar.setAlignment(QtCore.Qt.AlignRight)
        q_progress_bar.setRange(0, 100)
        q_progress_bar.setMaximumHeight(15)
        q_progress_bar.setMaximumWidth(200)
        q_progress_bar.setTextVisible(True)
        q_progress_bar.setFormat("Calculating...")
        q_progress_bar.setVisible(False)
        return q_progress_bar

    def display_complete_time(self, total_time):
        if total_time != 0.0:
            message = f"Completed in {total_time:.1f} seconds"
        else:
            message = "Complete..."
        self.q_right_label.setText(message)
        self.q_progress_bar.setVisible(False)
        self.q_right_label.setVisible(True)

    def display_progress(self, progress: float):
        progress_int_percentage = round(100*progress)
        self.q_progress_bar.setValue(progress_int_percentage)
        self.q_right_label.setVisible(False)
        self.q_progress_bar.setVisible(True)



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
        # self.q_right_label = self.make_right_label()
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

    # def make_right_label(self) -> QtWidgets.QLabel:
    #     q_right_label = QtWidgets.QLabel("Right text")
    #     # q_right_label.setMaximumWidth(200)
    #     q_right_label.setAlignment(QtCore.Qt.AlignCenter)
    #     return q_right_label

    def make_right_widget(self) -> QtWidgets.QWidget:
        q_right_widget = QtWidgets.QWidget()
        q_right_layout = QtWidgets.QHBoxLayout()
        q_right_widget.setLayout(q_right_layout)
        q_right_layout.setSpacing(0)
        q_right_layout.setContentsMargins(0, 0, 0, 0)
        q_right_spacer = QtWidgets.QLabel("")
        q_right_layout.addWidget(q_right_spacer)
        q_right_layout.addWidget(self.q_progress_bar)

        # return q_right_label
        return q_right_widget

    def make_progress_bar(self) -> QtWidgets.QProgressBar:
        q_progress_bar = QtWidgets.QProgressBar()
        q_progress_bar.setAlignment(QtCore.Qt.AlignRight)
        q_progress_bar.setRange(0, 100)
        q_progress_bar.setMaximumHeight(15)
        q_progress_bar.setMaximumWidth(200)
        q_progress_bar.setTextVisible(True)
        q_progress_bar.setFormat("Calculating...")
        # q_progress_bar.setAlignment(QtCore.Qt.AlignRight)
        return q_progress_bar

    def complete(self, total_time):
        if total_time != 0.0:
            message = f"Completed in {total_time:.4f} seconds"
        else:
            message = "Complete..."
        self.q_left_label.setText(message)
        # self.q_status_bar.showMessage(message)

from PyQt5 import QtWidgets, QtCore


class StatusBar:
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        # status_bar for main_window
        self.q_status_bar = QtWidgets.QStatusBar(q_main_window)
        q_main_window.setStatusBar(self.q_status_bar)

        # "normal" label added to status_bar
        self.q_left_label = self.make_left_label()
        # self.q_center_label = self.make_center_label()
        self.q_progress_bar = self.make_progress_bar()

        self.q_status_bar.addWidget(self.q_left_label)
        self.q_status_bar.addPermanentWidget(self.q_progress_bar)
        # self.q_status_bar.addWidget(self.q_center_label, 1)
        # self.q_status_bar.addPermanentWidget(self.q_center_label)

    def make_left_label(self) -> QtWidgets.QLabel:
        q_left_label = QtWidgets.QLabel("Left text")
        q_left_label.setAlignment(QtCore.Qt.AlignLeft)
        return q_left_label

    # def make_center_label(self) -> QtWidgets.QLabel:
    #     q_center_label = QtWidgets.QLabel("Center text")
    #     q_center_label.setAlignment(QtCore.Qt.AlignCenter)
    #     return q_center_label

    def make_progress_bar(self) -> QtWidgets.QProgressBar:
        q_progress_bar = QtWidgets.QProgressBar()
        q_progress_bar.setRange(0, 100)
        q_progress_bar.setMaximumHeight(15)
        q_progress_bar.setMaximumWidth(200)
        q_progress_bar.setTextVisible(True)
        q_progress_bar.setFormat("Calculating...")
        return q_progress_bar

    def complete(self, total_time):
        if total_time != 0.0:
            message = f"Completed in {total_time:.4f} seconds"
        else:
            message = "Complete..."
        self.q_status_bar.showMessage(message)

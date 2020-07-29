from PyQt5 import QtWidgets


class StatusBar:
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        # status_bar for main_window
        self.q_status_bar = QtWidgets.QStatusBar(q_main_window)
        q_main_window.setStatusBar(self.q_status_bar)

        # "normal" label added to status_bar
        self.q_hello_label = QtWidgets.QLabel("Hi, I'm a status bar")
        self.q_status_bar.addWidget(self.q_hello_label)

        self.q_progress_bar = QtWidgets.QProgressBar(self.q_status_bar)
        self.q_progress_bar.setRange(0, 100)
        # self.q_progress_bar.setGeometry(30, 40, 200, 25)
        self.q_progress_bar.setValue(50)
        self.q_progress_bar.setMaximumHeight(15)
        self.q_progress_bar.setMaximumWidth(200)
        self.q_progress_bar.setVisible(False)
        self.q_status_bar.addPermanentWidget(self.q_progress_bar)

    def complete(self, total_time):
        if total_time != 0.0:
            message = f"Completed in {total_time:.4f} seconds"
        else:
            message = "Complete..."
        self.q_status_bar.showMessage(message)

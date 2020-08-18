import platform
from PyQt5 import QtWidgets, QtGui, QtCore


class Clipboard:
    def __init__(self, application: QtWidgets.QApplication):
        self._q_clipboard: QtGui.QClipboard = application.clipboard()

    def copy_text(self, text: str):
        # from: https://www.medo64.com/2019/12/copy-to-clipboard-in-qt/
        self._q_clipboard.setText(text, QtGui.QClipboard.Clipboard)

        if self._q_clipboard.supportsSelection():
            self._q_clipboard.setText(text, QtGui.QClipboard.Selection)

        # Under Linux, sleep for 50ms to ensure text is copied to clipboard
        # Changed from 1 second in link
        if platform.system() == "Linux":
            QtCore.QThread.msleep(50)

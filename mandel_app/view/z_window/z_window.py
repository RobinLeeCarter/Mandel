from typing import Callable

from PyQt5 import QtWidgets, QtGui, QtCore

from mandel_app.view.z_window import actions


class ZWindow:
    def __init__(self, parent: QtWidgets.QMainWindow):
        self.q_main_window = XMainWindow(parent=parent)
        # Set some main window's properties
        self.q_main_window.setWindowTitle('Z Tracing')
        self.q_main_window.setGeometry(200, 200, 700, 700)

        stylesheet = self.get_stylesheet()
        self.q_main_window.setStyleSheet(stylesheet)

        self.is_active = False

        self.actions = actions.Actions(self.q_main_window)
        # self.menu = menu.Menu(self.q_main_window, self.actions.action_dict)
        # self.toolbars = toolbars.Toolbars(self.q_main_window, self.actions.action_dict)

        # self.toolbar = toolbar.Toolbar("My main toolbar", self.q_main_window)
        # self.central = central.Central(self.q_main_window)
        # self.status_bar = status_bar.StatusBar(self.q_main_window)

        # self.q_main_window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.q_main_window.show()
        self.q_main_window.setVisible(False)
        # self.central.set_image_space()

    def get_stylesheet(self):
        stylesheet = """
            background-color: darkGray
        """
        return stylesheet

    def hide(self):
        self.q_main_window.setVisible(False)

    def show(self):
        self.q_main_window.setVisible(False)
        self.q_main_window.setVisible(True)

    def set_on_key_pressed(self, on_key_pressed: Callable[[QtGui.QKeyEvent], None]):
        @QtCore.pyqtSlot()
        def slot(key_event: QtGui.QKeyEvent):
            on_key_pressed(key_event)

        # noinspection PyUnresolvedReferences
        self.q_main_window.keyPressSignal.connect(slot)

    def set_on_active(self, on_active: Callable[[], None]):
        @QtCore.pyqtSlot()
        def slot():
            if not self.is_active:
                on_active()

        # noinspection PyUnresolvedReferences
        self.q_main_window.activationChangeSignal.connect(slot)

    def set_on_close(self, on_close: Callable[[], None]):
        @QtCore.pyqtSlot()
        def slot():
            on_close()

        # noinspection PyUnresolvedReferences
        self.q_main_window.closeSignal.connect(slot)


class XMainWindow(QtWidgets.QMainWindow):
    keyPressSignal = QtCore.pyqtSignal(QtGui.QKeyEvent)
    activationChangeSignal = QtCore.pyqtSignal()
    closeSignal = QtCore.pyqtSignal()

    def keyPressEvent(self, key_event: QtGui.QKeyEvent) -> None:
        # noinspection PyUnresolvedReferences
        self.keyPressSignal.emit(key_event)
        super().keyPressEvent(key_event)

    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.ActivationChange and self.isActiveWindow():
            self.activationChangeSignal.emit()
        super().changeEvent(event)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if event.spontaneous():
            self.closeSignal.emit()
        super().closeEvent(event)

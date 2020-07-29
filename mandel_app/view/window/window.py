from typing import Callable

from PyQt5 import QtWidgets, QtGui, QtCore

from mandel_app.view import central
from mandel_app.view.window import actions, menu, toolbars, status_bar


class Window:
    def __init__(self):  # q_application: QtWidgets.QApplication
        # self.q_application = q_application
        self.q_main_window = XMainWindow()
        # Set some main window's properties
        self.q_main_window.setWindowTitle('Mandel App')
        self.q_main_window.setGeometry(50, 50, 1500, 1000)
        self.q_main_window.setFocusPolicy(QtCore.Qt.ClickFocus)

        stylesheet = self.get_stylesheet()
        self.q_main_window.setStyleSheet(stylesheet)

        self.actions = actions.Actions(self.q_main_window)
        self.menu = menu.Menu(self.q_main_window, self.actions.action_dict)
        self.toolbars = toolbars.Toolbars(self.q_main_window, self.actions.action_dict)

        self.central = central.Central(self.q_main_window)
        self.status_bar = status_bar.StatusBar(self.q_main_window)

        # modes
        self.is_full_screen = False
        self.is_active = True

        self.q_main_window.show()
        self.central.set_image_space()

    def get_stylesheet(self):
        stylesheet = """
            background-color: darkGray
        """
        return stylesheet

    def set_full_screen(self, full_screen: bool):
        self.is_full_screen = full_screen
        if full_screen:
            self.q_main_window.showFullScreen()
            self.toolbars.full_screen_hide()
            self.menu.full_screen_hide()
            self.status_bar.q_status_bar.hide()
        else:
            self.q_main_window.showNormal()
            self.toolbars.full_screen_show()
            self.menu.full_screen_show()
            self.status_bar.q_status_bar.show()

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


class XMainWindow(QtWidgets.QMainWindow):
    keyPressSignal = QtCore.pyqtSignal(QtGui.QKeyEvent)
    activationChangeSignal = QtCore.pyqtSignal()

    def keyPressEvent(self, key_event: QtGui.QKeyEvent) -> None:
        # noinspection PyUnresolvedReferences
        self.keyPressSignal.emit(key_event)
        super().keyPressEvent(key_event)

    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.ActivationChange and self.isActiveWindow():
            self.activationChangeSignal.emit()
        super().changeEvent(event)

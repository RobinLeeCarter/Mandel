from typing import Callable

from PyQt5 import QtGui, QtWidgets

from mandel_app.view import widgets
from mandel_app.view.window import actions, menu, toolbars, status_bar, central


class Window:
    def __init__(self, application_name: str, window_settings: dict):
        self._application_name: str = application_name

        self.q_main_window: widgets.XMainWindow = widgets.XMainWindow()
        # modes
        self.is_full_screen = False
        self.is_active = True

        self.actions: actions.Actions = actions.Actions(self.q_main_window)
        self.menu: menu.Menu = menu.Menu(self.q_main_window, self.actions.action_dict)
        self.toolbars: toolbars.Toolbars = toolbars.Toolbars(self.q_main_window, self.actions.action_dict)

        self.central: central.Central = central.Central(self.q_main_window)
        self.status_bar: status_bar.StatusBar = status_bar.StatusBar(self.q_main_window)

        self._build(window_settings)
        self.central.refresh_image_space()

    def _build(self, window_settings: dict):
        # Set some main window's properties
        self.q_main_window.setWindowTitle(self._application_name)
        self.q_main_window.resize(window_settings["size"])
        self.q_main_window.move(window_settings["pos"])
        self.q_main_window.setMinimumSize(200, 200)

        stylesheet = self._get_stylesheet()
        self.q_main_window.setStyleSheet(stylesheet)
        self.q_main_window.show()

    def _get_stylesheet(self):
        stylesheet = """
            background-color: darkGray
        """
        return stylesheet

    def get_dpi(self) -> int:
        q_application = QtWidgets.QApplication.instance()   # get singleton
        screen: QtGui.QScreen = q_application.screens()[0]
        dpi = round(screen.physicalDotsPerInch())
        # print(f"dpi = {dpi}")
        return dpi

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

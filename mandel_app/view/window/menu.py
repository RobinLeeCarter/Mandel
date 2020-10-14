from typing import List, Dict

from PyQt5 import QtWidgets

from mandel_app.view.window import actions


class Menu:
    def __init__(self, q_main_window: QtWidgets.QMainWindow, action_dict: Dict[str, QtWidgets.QAction]):
        self._q_main_window: QtWidgets.QMainWindow = q_main_window
        self._action_dict: Dict[str, QtWidgets.QAction] = action_dict
        self.q_menu_bar: QtWidgets.QMenuBar = self._q_main_window.menuBar()

        # self.file_menu: QtWidgets.QMenu = self._q_menu_bar.addMenu("&File")
        # self._add_actions(self.file_menu, ["load", "save", "close"])

        self._view_menu: QtWidgets.QMenu = self.q_menu_bar.addMenu("&View")
        self._add_actions(self._view_menu, ["full_screen", "z_mode", "julia_mode", "max_iterations"])

    def _add_actions(self, menu_: QtWidgets.QMenu, action_names: List[str]):
        for action_name in action_names:
            menu_.addAction(self._action_dict[action_name])

    def full_screen_hide(self):
        self.q_menu_bar.hide()

    def full_screen_show(self):
        self.q_menu_bar.show()


# test script
if __name__ == "__main__":
    q_application = QtWidgets.QApplication([])
    main_window = QtWidgets.QMainWindow()
    actions = actions.Actions(main_window)
    menu = Menu(main_window, actions.action_dict)
    print("done")

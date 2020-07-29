from abc import ABC

from PyQt5 import QtWidgets

from mandel_app.view import action


class Actions(ABC):
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        self._q_main_window = q_main_window
        self.action_dict = {}

    def _add_action(self, action_: action.Action):
        self.action_dict[action_.name] = action_.q_action

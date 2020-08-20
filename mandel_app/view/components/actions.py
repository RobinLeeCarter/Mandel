from abc import ABC
from typing import Dict

from PyQt5 import QtWidgets

from mandel_app.view.components import action


class Actions(ABC):
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        self._q_main_window: QtWidgets.QMainWindow = q_main_window
        self.action_dict: Dict[str, QtWidgets.QAction] = {}

    def _add_action(self, action_: action.Action):
        self.action_dict[action_.name] = action_.q_action

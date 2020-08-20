from typing import Optional

from PyQt5 import QtGui

import utils
_ICON_PATH = r"resources/icons/"


class Icon:
    def __init__(self, icon_filename: Optional[str] = None):
        self.q_icon: Optional[QtGui.QIcon] = None
        if icon_filename is not None:
            self.load_icon(icon_filename)

    def load_icon(self, icon_filename: str):
        self.q_icon = QtGui.QIcon(utils.full_path(_ICON_PATH + icon_filename))

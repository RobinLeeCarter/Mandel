from PyQt5 import QtWidgets, QtGui


# This disables the scroll-wheel since we are using it for zooming
# plus the scrollbars are disabled
# removing the QScrollArea altogether messed up the image rendering and it was so hard to get right the first time
class XScrollArea(QtWidgets.QScrollArea):

    def wheelEvent(self, wheel_event: QtGui.QWheelEvent) -> None:
        wheel_event.ignore()

from __future__ import annotations
import sys
import platform

# import gc
from typing import Optional

from PyQt5 import QtWidgets

import thread
from mandel_app import model, view, controller, gpu


class Application:
    _instance: Optional[Application] = None

    def __new__(cls, *args, **kwargs):
        assert cls._instance is None, "Singleton Controller is already instantiated"
        instance = super().__new__(cls)
        cls._instance = instance
        return instance

    @classmethod
    def instance(cls) -> Application:
        return cls._instance

    def __init__(self):
        self.application_name: str = "Mandlebrot Explorer"
        self.organization_name: str = "Robin Carter Industries"
        self._os: str = platform.system()

        self._application: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
        self._model: model.Model = model.Model()
        self._view: view.View = view.View(self._application, self.application_name)
        self._controller: controller.Controller = controller.Controller(self._model, self._view)
        self._gpu: gpu.Gpu = gpu.Gpu()

        self.build()

    def build(self):
        self._application.setOrganizationName(self.organization_name)
        self._application.setApplicationName(self.application_name)

        # enable model and view to send messages to controller
        self._model.set_controller(self._controller)
        self._view.set_controller(self._controller)

        self._controller.build()

        sys.exit(self._application.exec_())

    # constrained access to singleton objects like Gpu
    def set_thread_state(self, thread_state: thread.state):
        self._gpu.set_thread_state(thread_state)

    @property
    def gpu_ready(self):
        return self._gpu.ready

    @property
    def has_cuda(self):
        return self._gpu.has_cuda

    @property
    def os(self):
        return self._os


def launch_application():
    # gc.disable()
    Application()

from __future__ import annotations
from typing import Callable, Optional, Generator
from abc import ABC, abstractmethod

from PyQt5 import QtWidgets

from thread.progress_estimator import ProgressEstimator


class Job(ABC):
    # region Setup
    def __init__(self):
        self.job_number: int = 0
        self._in_progress: bool = False
        self.stop_requested: bool = False
        self.progress_estimator: Optional[ProgressEstimator] = None
        self._job_checkpoint: Optional[Callable[[Job, float], None]] = None

    def set_job_checkpoint(self, job_checkpoint: Callable[[Job, float], None]):
        self._job_checkpoint = job_checkpoint

    @property
    def in_progress(self) -> bool:
        return self._in_progress
    # endregion

    # region Run
    def run(self):
        self._in_progress = True
        if self.progress_estimator:
            self.progress_estimator.start()
            for yielded in self._exec():
                self._check_if_stop_requested()
                if not self._in_progress:
                    return
                else:
                    self.progress_estimator.estimate_progress(yielded)
                    self._job_checkpoint(self, self.progress_estimator.progress)
            self.progress_estimator.stop()
        else:
            for _ in self._exec():
                self._check_if_stop_requested()
                if not self._in_progress:
                    return
                # self._job_checkpoint(self)
                # if self.stop_requested:
                #     self._in_progress = False
                #     return
        self._in_progress = False
        print("run end")

    @abstractmethod
    def _exec(self) -> Generator[float, None, None]:
        pass

    def _check_if_stop_requested(self):
        # let the thread event-queue run so this job can be requested to be stopped
        QtWidgets.QApplication.processEvents()
        if self.stop_requested:
            self._in_progress = False
    # endregion

    # @abc.abstractmethod
    # def follow_on_actions(self):
    #     pass

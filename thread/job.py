from __future__ import annotations
from typing import Callable, Optional, Generator
from abc import ABC, abstractmethod

from thread.progress_estimator import ProgressEstimator


class Job(ABC):
    # region Setup
    def __init__(self):
        self.job_number: int = 0
        self.interrupt_requested: bool = False
        self.progress_estimator: Optional[ProgressEstimator] = None
        self._job_checkpoint: Optional[Callable[[Job, float], None]] = None

    def set_job_checkpoint(self, job_checkpoint: Callable[[Job, float], None]):
        self._job_checkpoint = job_checkpoint
    # endregion

    # region Run
    def run(self):
        if self.progress_estimator:
            self.progress_estimator.start()
            for yielded in self._exec():
                self.progress_estimator.estimate_progress(yielded)
                self._job_checkpoint(self, self.progress_estimator.progress)
                if self.interrupt_requested:
                    return
            self.progress_estimator.stop()
        else:
            for _ in self._exec():
                self._job_checkpoint(self)
                if self.interrupt_requested:
                    return

    @abstractmethod
    def _exec(self) -> Generator[float, None, None]:
        pass
    # endregion

    # @abc.abstractmethod
    # def follow_on_actions(self):
    #     pass

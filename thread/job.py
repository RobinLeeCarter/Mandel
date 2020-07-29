from __future__ import annotations
import copy
from typing import Callable, Union, Optional, Generator
import abc

from thread.progress_estimator import ProgressEstimator


class Job:
    # region Setup
    def __init__(self,
                 data: Union[tuple, object, None] = None,
                 **kwargs):
        self.job_number: int = 0
        self.interrupt_requested: bool = False

        self.progress_estimator: Optional[ProgressEstimator] = None

        self._job_checkpoint: Optional[Callable[[Job, float], None]] = None

        # if any data,
        # make and keep hold of a copy of it until the Job is worked
        # and then pass it in to the call
        self._data: tuple
        if data is None:
            self._data = tuple()
        elif isinstance(data, tuple):
            self._data = copy.deepcopy(data)
        else:   # therefore object
            self._data = (copy.deepcopy(data), )

        self._kwargs: dict = kwargs

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

    @abc.abstractmethod
    def _exec(self) -> Generator[float, None, None]:
        pass
    # endregion

    # region Results
    def get_data(self) -> Union[tuple, object, None]:
        if len(self._data) == 0:
            return None
        elif len(self._data) == 1:
            return self._data[0]
        else:
            return self._data
    # endregion

    # @abc.abstractmethod
    # def follow_on_actions(self):
    #     pass

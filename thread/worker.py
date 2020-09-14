from typing import List, Optional

# import cupy as cp
from PyQt5 import QtWidgets, QtCore

from thread import job, enums


class Worker(QtCore.QObject):
    progressUpdate = QtCore.pyqtSignal(float, int)
    jobComplete = QtCore.pyqtSignal(job.Job)

    activeChange = QtCore.pyqtSignal(bool)
    stopSuccess = QtCore.pyqtSignal()
    debugMessage = QtCore.pyqtSignal(str)

    # region Setup
    def __init__(self):
        super().__init__()
        # 0 is the front of the queue, the current job is the only at the front of the queue
        # a job must always be on the queue before calling do_job
        self._job_queue: List[job.Job] = []
        self._job_number: int = 0
        self._queue_active: bool = False
        self._worker_active: bool = False

    # region Slots for Manager
    def request_job(self,
                    job_: job.Job,
                    queue_as: enums.QueueAs
                    ):
        self._job_number += 1
        job_.job_number = self._job_number
        job_.set_job_checkpoint(self._job_checkpoint)

        if queue_as == enums.QueueAs.ENQUEUE:
            # join the back of the queue and waits it's turn
            self._job_queue.append(job_)
        elif queue_as == enums.QueueAs.EXPEDITE:
            # add to this job to the front of the queue
            self._job_queue.insert(0, job_)
            # do this job leaving the previous current job partially completed
            self._do_job(job_)
            # so can then continue with previous job that was in progress or the next in the queue
        elif queue_as == enums.QueueAs.SINGULAR:
            # Command to just run this job and get rid of all the others as quickly as possible
            # request all other jobs to stop
            # add this job to be next in the queue
            self.request_stop()
            self._job_queue.append(job_)

        if not self._queue_active and len(self._job_queue) > 0:
            self._do_job_queue()

    def request_stop(self):
        # request to stop the current job if there is one and if running
        # clear the rest of the queue
        if self._job_queue:
            current_job = self._job_queue[0]
            self._job_queue.clear()
            if current_job.in_progress:
                # rebuild job_queue as just the current job and request it to stop
                self._job_queue.append(current_job)
                current_job.stop_requested = True
    # endregion

    # region Job Processing
    def _do_job_queue(self):
        current_job: Optional[job.Job] = None
        self._queue_active = True
        while self._job_queue:
            current_job = self._job_queue[0]
            self._do_job(current_job)
        self._queue_active = False

        # if the final job in the queue was requested to stop then that was a full stop request so emit stopSuccess
        if current_job is not None and current_job.stop_requested:
            self.stopSuccess.emit()

    def _set_active(self, active: bool):
        if active != self._worker_active:
            self._worker_active = active
            self.activeChange.emit(active)

    def _do_job(self, job_: job.Job):
        # TODO: This assert error fired once
        # assert job_ in self._job_queue, "job_ not in _job_queue"
        self._set_active(True)
        job_.run()
        # let the thread event-queue run so this job can be requested to be stopped
        QtWidgets.QApplication.processEvents()
        # job is always removed from the queue at the end (so it must always be added else this will fail)
        # TODO: remove this workaround
        if job_ in self._job_queue:
            self._job_queue.remove(job_)
        # if this was the last job set the worker to inactive
        if not self._job_queue:
            # stream_done = cp.cuda.get_current_stream().done
            # if not stream_done:
            #     print(f"last job stream_done: {stream_done}")
            self._set_active(False)
        # if the job was requested to be stopped then we don't want the actions associated with the job completing
        if not job_.stop_requested:
            self.jobComplete.emit(job_)

    def _job_checkpoint(self, job_: job.Job, progress: float = 0.0):
        if job_.progress_estimator:
            self.progressUpdate.emit(progress, job_.job_number)
        # let the thread event-queue run so this job can be requested to be stopped
        QtWidgets.QApplication.processEvents()
        # if it does stop execution will re-emerge in _do_job after job_.run()
    # endregion

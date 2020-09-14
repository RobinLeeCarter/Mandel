from typing import Optional, Callable

from PyQt5 import QtWidgets, QtCore

from thread import worker, job, enums, state


class Manager(QtCore.QObject):
    _request_job = QtCore.pyqtSignal(job.Job, enums.QueueAs)
    _request_stop = QtCore.pyqtSignal()

    # region Setup
    def __init__(self,
                 on_progress_update: Optional[Callable[[job.Job, int], None]] = None,
                 # on_active_change: Optional[Callable[[bool], None]] = None,
                 on_stop_success: Optional[Callable[[], None]] = None,
                 on_job_complete: Optional[Callable[[job.Job], None]] = None
                 ):
        super().__init__()
        self._thread: QtCore.QThread = QtCore.QThread()
        self._worker: worker.Worker = worker.Worker()
        self._state: state.State = state.State()
        # self._worker_active: bool = False
        self._on_progress_update: Optional[Callable[[float, int], None]] = on_progress_update
        # self._on_active_change: Optional[Callable[[bool], None]] = on_active_change
        self._on_stop_success: Optional[Callable[[], None]] = on_stop_success
        self._on_job_complete: Optional[Callable[[job.Job], None]] = on_job_complete

        self._singular_job: Optional[job.Job] = None

    # @property
    # def worker_active(self) -> bool:
    #     return self._state.worker_active

    @property
    def state(self) -> state.State:
        return self._state
    # endregion

    # region Requests from main thread
    def start_thread(self):
        # move worker to thread and make sure it is deleted when the thread is finished
        self._worker.moveToThread(self._thread)
        self._thread.finished.connect(self._worker.deleteLater)   # seems to get deleted anyway though

        # make connections across threads (gui <-> worker)
        # gui -> worker
        self._request_job.connect(self._worker.request_job)
        self._request_stop.connect(self._worker.request_stop)
        # worker -> gui
        self._worker.progressUpdate.connect(self.progress_update_slot)
        self._worker.activeChange.connect(self.active_change_slot)
        self._worker.stopSuccess.connect(self.stop_success_slot)
        self._worker.jobComplete.connect(self.job_complete_slot)
        self._worker.debugMessage.connect(self.debug_message)

        # more reliable than def __del__ in python as may not be called
        QtWidgets.QApplication.instance().aboutToQuit.connect(self.quit_thread)
        self._thread.start()

    def request_job(self, job_: job.Job, queue_as: enums.QueueAs):
        if queue_as == enums.QueueAs.SINGULAR:
            self._singular_job = job_
            # print(f"singular_job.id = {id(self._singular_job)}")
        self._request_job.emit(job_, queue_as)

    def request_stop(self):
        self._request_stop.emit()
    # endregion

    # region Slots for Worker
    def progress_update_slot(self, job_: job.Job,  progress: float):
        if self._on_progress_update is not None:
            self._on_progress_update(job_, progress)

    def active_change_slot(self, active: bool):
        self._state.worker_active = active
        # if self._on_active_change is not None:
        #     self._on_active_change(active_change)

    def stop_success_slot(self):
        if self._on_stop_success is not None:
            self._singular_job = None
            self._on_stop_success()

    def job_complete_slot(self, job_: job.Job):
        if self._on_job_complete is not None:
            if self._singular_job:
                if job_ is self._singular_job:
                    # print(f"same job {id(job_)} is {id(self._singular_job)}")
                    self._on_job_complete(job_)
                    self._singular_job = None
            else:
                self._on_job_complete(job_)

    def quit_thread(self):
        self._thread.quit()
        self._thread.wait()

    def debug_message(self, message: str):
        print(message)
    # endregion

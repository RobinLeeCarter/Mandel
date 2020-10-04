from typing import Optional

import utils
import thread


class Gpu(utils.Gpu):
    def __init__(self):
        super().__init__()
        self.thread_state: Optional[thread.State] = None

    def set_thread_state(self, thread_state: thread.State):
        self.thread_state = thread_state

    @property
    def ready(self) -> bool:
        if not self._has_cuda:
            return False

        if self.thread_state is None:
            return self.stream_ready
        else:
            return self.stream_ready or self.thread_state.worker_active

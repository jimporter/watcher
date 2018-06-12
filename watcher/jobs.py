import bisect
import functools
import time


@functools.total_ordering
class Job:
    def __init__(self, fn, interval):
        self.fn = fn
        self.interval = interval
        self.next_time = time.time()
        self.next_args = ()

    def __lt__(self, rhs):
        self.next_time < rhs.next_time

    def run(self):
        self.next_args = self.fn(*self.next_args) or ()
        self.next_time += self.interval


class JobQueue:
    def __init__(self):
        self._queue = []

    def add(self, fn, interval):
        j = Job(fn, interval)
        bisect.insort(self._queue, j)

    def run(self):
        while True:
            next_job = self._queue.pop(0)
            now = time.time()
            if next_job.next_time > now:
                time.sleep(next_job.next_time - now)
            next_job.run()
            bisect.insort(self._queue, next_job)

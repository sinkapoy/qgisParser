from multiprocessing import Process
import time

class ThreadProvider:
    threads: list[Process] = []
    max_threads = 4

    def wait(self):
        while (len(self.threads) >= self.max_threads):
            for thread in self.threads:
                if (not thread.is_alive()):
                    self.threads.remove(thread)

            if (len(self.threads) >= self.max_threads):
                time.sleep(0.01)

    def add_thread(self, thread: Process):
        self.threads.append(thread)
import multiprocessing
import logging
#TODO: Add pluggable error handler for Hive and for Workers

class WorkerNotReadyException(Exception):
    pass

class Hive(object):
    def __init__(self, name, worker_count):
        self.name = name
        self.pool = multiprocessing.Pool(worker_count)

    def run(self, workers):
        active_workers = set(w for w in workers if len(w.depends_on) == 0)
        for worker in active_workers:
            logging.info("Task begun in hive %r (%r), worker %r (%r)", self.name, self, worker.name, worker)
            worker.buzz()
        while len(active_workers) > 0:
            finished_workers = set()
            new_workers = set()
            for worker in active_workers:
                if worker.task_error:
                    logging.error("An error occurred in hive %r (%r), worker %r (%r)", self.name, self, worker.name, worker)
                    finished_workers.add(worker)
                if worker.task_completed:
                    logging.info("Task completed in hive %r (%r), worker %r (%r)", self.name, self, worker.name, worker)
                    for receiver in (w for w in workers if worker in w.depends_on): 
                        receiver.buzz()
                        logging.info("Task buzzed in hive %r (%r), worker %r (%r)", self.name, self, receiver.name, receiver)
                        new_workers.add(receiver)
                    finished_workers.add(worker)
            for w in finished_workers: active_workers.remove(w)
            active_workers.update(new_workers)
        
class Worker(object):
    def __init__(self, name, hive, task, depends_on = []):
        self.name = name
        self.hive = hive
        self.task = task
        self.depends_on = depends_on
        self.task_started = False
        self.task_completed = False
        self.task_error = False
        self.result = None
        self.error = None
        self.process = None

    def buzz(self):
        try:
            # check if all dependencies have completed
            feeds = [f.regurgitate() for f in self.depends_on]
            self.run(feeds)
        except WorkerNotReadyException:
            pass

    def run(self, feeds):
        if not self.task_started:
            self.task_started = True
            self.process = self.hive.pool.apply_async(func=self.task, args=(feeds,), 
                              callback=self.store_result, 
                              error_callback=self.store_error)

    def store_result(self, result):
        self.result = result
        self.task_completed = True

    def store_error(self, exception):
        self.error = exception
        self.task_error = True

    def regurgitate(self):
        """This will return the already determined result of the task or if not available will attempt to start the task and then throw an exception"""
        if self.task_completed:
            return self.result
        self.buzz()
        raise WorkerNotReadyException
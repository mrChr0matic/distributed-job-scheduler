from collections import deque
from src.base.worker import Worker
from src.base.dag import DAG
from concurrent.futures import ThreadPoolExecutor, as_completed

def init_workers(worker_count):
    worker_pool = deque()
    for _ in range(worker_count):
        worker = Worker()
        worker_pool.append(worker)
    return worker_pool

class Scheduler:
    def __init__(self, worker_count = 3):
        self.task_queue = deque()
        self.worker_pool = init_workers(worker_count)
        self.busy_workers = deque()
        self.worker_count = worker_count
        self.running = False
        self.dag = DAG()
        self.task_directory = {}
    
    def is_running(self):
        return self.running
    
    def cancel_task(self, task_id):
        task = self.task_directory[task_id]
        if task.get_state() == "PENDING":
            task.state_machine.change_state("CANCELLED")
        elif task.get_state() == "QUEUED":
            task.state_machine.change_state("CANCELLED")
            self.task_queue.remove(task)
        elif task.get_state() == "RUNNING":
            ...
        else:
            ...
        
    def submit_task(self, task):
        if task.task_id in self.task_directory:
            raise ValueError("Task already submitted")
        self.task_directory[task.task_id] = task
        self.dag.add_task(task.task_id)
        
    def set_task_dependency(self, pre_task, post_task):
        self.dag.add_edge(pre_task.task_id, post_task.task_id)
    
    def _is_ready(self, task):
        if task.get_state() != "PENDING":
            return False
        for pre_task in self.dag.depends[task.task_id]:
            if self.task_directory[pre_task].get_state()!='SUCCESS':
                return False
        return True

    def get_ready_tasks(self):
        ready_list = []
        for task_id in self.dag.depends:
            if self._is_ready(self.task_directory[task_id]):
                ready_list.append(self.task_directory[task_id])
        return ready_list
    
    def enqueue_ready_tasks(self):
        for task in self.get_ready_tasks():
            task.state_machine.change_state("QUEUED")
            self.task_queue.append(task)
        
    def run_task(self, task, worker):
        return worker.execute_task(task)
    
    def run_all_tasks(self):
        self.running = True
        try:
            with ThreadPoolExecutor(max_workers=self.worker_count) as executor:
                futures = {}
                self.enqueue_ready_tasks()
                while self.task_queue and self.worker_pool:
                    task = self.task_queue.popleft()
                    worker = self.worker_pool.popleft()
                    
                    self.busy_workers.append(worker)
                    future = executor.submit(self.run_task, task, worker)
                    
                    futures[future] = (worker, task)
                    
                while futures:
                    future = next(as_completed(futures))
                    worker, task = futures.pop(future)
                    try:
                        future.result()
                    except Exception:
                        if task.can_retry():
                            task.increment_retry()
                            task.state_machine.change_state('QUEUED')
                            self.task_queue.append(task)
                    finally:
                        self.busy_workers.remove(worker)
                        
                    self.enqueue_ready_tasks() 
                    
                    if self.task_queue:
                        next_task = self.task_queue.popleft()                        
                        self.busy_workers.append(worker)
                        new_future = executor.submit(self.run_task, next_task, worker)
                        
                        futures[new_future] = (worker, next_task)
                    else:
                        self.worker_pool.append(worker)
        finally:
            self.running = False
from collections import deque

class Scheduler:
    def __init__(self):
        self.task_queue = deque()
    def submit_task(self, task):
        task.state_machine.change_state('QUEUED')
        self.task_queue.append(task)
    def run(self):
        pass
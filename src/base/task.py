import uuid
from pathlib import Path
from src.base.state_machine import StateMachine

MAX_RETRY = 2

class Task:
    def __init__(self, inputs, function = None, src_file = None):
        self.inputs = inputs
        self.task_id = uuid.uuid4()
        self.src_file = src_file
        self.function = function
        self.retry_count = 0
        self.state_machine = StateMachine()
        self.task_out = None
        if self.src_file and not Path(self.src_file).is_file():
                    raise FileNotFoundError(f"Source file not found: {self.src_file}")
        if (self.src_file and self.function) or (not self.src_file and not self.function):
            print("need atleast 1 function or src_file")
            raise ValueError("Task requires exactly one of function or src_file")
        
    def get_state(self):
        return self.state_machine.get_state()  
    
    def increment_retry(self):
        self.retry_count += 1
    
    def can_retry(self):
        return self.retry_count < MAX_RETRY
        
    def get_out(self):
        if self.state_machine.get_state() != "SUCCESS":
            raise RuntimeError(f"Task {self.task_id} has not completed successfully")
        return self.task_out
        
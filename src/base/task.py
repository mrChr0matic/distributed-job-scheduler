import uuid
from pathlib import Path
import importlib.util


def add(**inputs):
    return sum(inputs.values())

def sub(**inputs):
    values = list(inputs.values())
    result = values[0]
    for value in values[1:]:
        result -= value
    return result

func_map = {
    "add" : add,
    "sub" : sub
}

def execute_src(file_path: str, inputs: dict):
    spec = importlib.util.spec_from_file_location("task_module", file_path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load source file: {file_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "execute"):
        raise AttributeError(
            f"Source file {file_path} must contain an 'execute' function"
        )

    return module.execute(**inputs)

class Task:
    def __init__(self, inputs, function = None, src_file = None):
        self.inputs = inputs
        self.task_id = uuid.uuid4()
        self.state = "PENDING"
        self.src_file = src_file
        self.function = function
        if self.src_file and not Path(self.src_file).is_file():
                    raise FileNotFoundError(f"Source file not found: {self.src_file}")
        if (self.src_file and self.function) or (not self.src_file and not self.function):
            print("need atleast 1 function or src_file")
            raise ValueError("Task requires exactly one of function or src_file")
        
    def get_state(self):
        return self.state  
    
    def execute_task(self):
        self.state = 'RUNNING'
        try:
            out = None
            
            if self.src_file:
                out = execute_src(self.src_file, self.inputs)
            elif self.function:
                if self.function not in func_map.keys():
                    print(f"attempted function {self.function} does not exist")
                    raise ValueError(f"Unknown function: {self.function}")
                out = func_map.get(self.function)(**self.inputs)
                
            self.state = 'SUCCESS'
            self.task_out = out
            return self.state
        
        except Exception as e:
            print(f"{self.task_id} failed with error {repr(e)}")
            self.state = 'FAILED'
            raise
        
        
    def get_out(self):
        if self.state != "SUCCESS":
            raise RuntimeError(f"Task {self.task_id} has not completed successfully")
        return self.task_out
        
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

class Worker:
    def execute_task(self, task):
        task.state_machine.change_state('RUNNING')
        try:
            out = None
            if task.src_file:
                out = execute_src(task.src_file, task.inputs)
            elif task.function:
                if task.function not in func_map:
                    raise ValueError(f"Unknown function: {task.function}")
                out = func_map.get(task.function)(**task.inputs)
            task.state_machine.change_state('SUCCESS')
            task.task_out = out
            return task.state_machine.get_state()
        
        except Exception as e:
            print(f"{task.task_id} failed with error {repr(e)}")
            task.state_machine.change_state('FAILED')
            raise
            
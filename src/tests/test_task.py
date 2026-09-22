from src.base.task import Task
from src.base.scheduler import Scheduler
from src.base.worker import Worker
import pytest
from multiprocessing import Queue


def test_add_task():
    task = Task(
        inputs={"a" : 1, "b" : 2},
        function="add"   
    )
    
    assert task.get_state() == "PENDING"
    scheduler = Scheduler()
    worker = Worker()
    
    scheduler.submit_task(task)
    scheduler.enqueue_ready_tasks()
    worker.execute_task(scheduler.task_queue.popleft())
    
    assert task.get_state() == "SUCCESS"
    assert task.task_out == 3

def test_sub_task():
    task = Task(
        inputs={"a": 10, "b": 3, "c": 2},
        function="sub"
    )

    assert task.get_state() == "PENDING"

    scheduler = Scheduler()
    worker = Worker()
    
    scheduler.submit_task(task)
    scheduler.enqueue_ready_tasks()
    worker.execute_task(scheduler.task_queue.popleft())
        

    assert task.get_state() == "SUCCESS"
    assert task.get_out() == 5
    
def test_unknown_function():
    task = Task(
        inputs={"a": 10, "b": 3},
        function="multiply"
    )

    assert task.get_state() == "PENDING"
    
    scheduler = Scheduler()
    worker = Worker()
    
    scheduler.submit_task(task)
    scheduler.enqueue_ready_tasks()

    with pytest.raises(ValueError):
        worker.execute_task(scheduler.task_queue.popleft())

    assert task.get_state() == "FAILED"
    
def test_no_execution_mechanism():
    with pytest.raises(ValueError):
        Task(
            inputs={"a": 10, "b": 3}
        )
        
def test_multiple_execution_mechanisms():
    with pytest.raises(ValueError):
        Task(
            inputs={"a": 10},
            function="add",
            src_file="src/base/task.py"
        )

def test_missing_source_file():
    with pytest.raises(FileNotFoundError):
        Task(
            inputs={"a": 10},
            src_file="something.py"
        )

def test_valid_file():
    task = Task(
        inputs={"a": 10},
        src_file="src/modules/echo.py"
    )
    
    scheduler = Scheduler()
    worker = Worker()
    
    scheduler.submit_task(task)
    scheduler.enqueue_ready_tasks()
    
    worker.execute_task(scheduler.task_queue.popleft())
    assert task.get_state() == "SUCCESS"
    assert task.get_out() == {"a": 10}
    
def test_task_cannot_execute_twice():
    task = Task(
        inputs={"a": 1, "b": 2},
        function="add"
    )

    scheduler = Scheduler()
    worker = Worker()
    
    scheduler.submit_task(task)
    scheduler.enqueue_ready_tasks()
    
    worker.execute_task(scheduler.task_queue.popleft())

    with pytest.raises(ValueError):
        worker.execute_task(task)

    assert task.get_state() == "SUCCESS"
    
def test_task_can_be_serialized():
    task = Task(
        inputs={"a": 1, "b": 2},
        function="add"
    )

    queue = Queue()
    queue.put(task)

    received_task = queue.get()

    assert received_task.task_id == task.task_id
    assert received_task.inputs == task.inputs
    assert received_task.function == task.function
    assert received_task.get_state() == "PENDING"
from base.task import Task
from base.scheduler import Scheduler
from base.worker import Worker
import pytest

def test_add_task():
    task = Task(
        inputs={"a" : 1, "b" : 2},
        function="add"   
    )
    
    assert task.get_state() == "PENDING"
    scheduler = Scheduler()
    worker = Worker()
    
    scheduler.submit_task(task)
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
    worker.execute_task(scheduler.task_queue.popleft())

    with pytest.raises(ValueError):
        worker.execute_task(task)

    assert task.get_state() == "SUCCESS"
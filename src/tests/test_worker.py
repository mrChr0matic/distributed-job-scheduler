import pytest
from src.base..task import Task
from src.base..worker import Worker
from multiprocessing import Process, Queue

def test_worker_executes_task():
    task = Task(
        inputs={"a": 1, "b": 2},
        function="add"
    )

    worker = Worker()

    task.state_machine.change_state("QUEUED")

    worker.execute_task(task)

    assert task.get_state() == "SUCCESS"
    assert task.get_out() == 3


def test_worker_fails_task():
    task = Task(
        inputs={"a": 1, "b": 2},
        function="multiply"
    )

    worker = Worker()

    task.state_machine.change_state("QUEUED")

    with pytest.raises(ValueError):
        worker.execute_task(task)
    
    with pytest.raises(RuntimeError):
        task.get_out()

    assert task.get_state() == "FAILED"


def test_worker_cannot_execute_pending_task():
    task = Task(
        inputs={"a": 1, "b": 2},
        function="add"
    )

    worker = Worker()

    with pytest.raises(ValueError):
        worker.execute_task(task)

    assert task.get_state() == "PENDING"


def test_worker_cannot_execute_completed_task():
    task = Task(
        inputs={"a": 1, "b": 2},
        function="add"
    )

    worker = Worker()

    task.state_machine.change_state("QUEUED")
    worker.execute_task(task)

    assert task.get_state() == "SUCCESS"

    with pytest.raises(ValueError):
        worker.execute_task(task)

    assert task.get_state() == "SUCCESS"

def test_worker_with_module():
    task = Task(
        inputs={"a": 10},
        src_file="src/modules/echo.py"
    )
    task.state_machine.change_state('QUEUED')
    
    worker = Worker()
    
    worker.execute_task(task)
    assert task.get_state() == "SUCCESS"
    assert task.get_out() == {"a": 10}
    
def worker_process(task_queue, result_queue):
    worker = Worker()

    task = task_queue.get()

    worker.execute_task(task)

    result_queue.put(task)

def test_worker_process_executes_task():
    task_queue = Queue()
    result_queue = Queue()

    task = Task(
        inputs={"a": 1, "b": 2},
        function="add"
    )

    process = Process(
        target=worker_process,
        args=(task_queue, result_queue)
    )

    process.start()

    task.state_machine.change_state("QUEUED")
    task_queue.put(task)

    result = result_queue.get()

    process.join()

    assert result.task_id == task.task_id
    assert result.get_state() == "SUCCESS"
    assert result.task_out == 3
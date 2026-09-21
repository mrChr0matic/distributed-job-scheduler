import pytest
from base.task import Task
from base.worker import Worker

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
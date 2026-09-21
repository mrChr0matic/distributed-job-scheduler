import pytest
from base.task import Task
from base.scheduler import Scheduler
from base.worker import Worker

def test_submit_task():
    task = Task(
        inputs={"a": 1, "b": 2},
        function="add"
    )

    scheduler = Scheduler()

    scheduler.submit_task(task)

    assert task.get_state() == "QUEUED"
    assert len(scheduler.task_queue) == 1
    assert scheduler.task_queue[0] == task
    
def test_submit_completed_task():
    task = Task(
        inputs={"a": 1, "b": 2},
        function="add"
    )
    scheduler = Scheduler()
    worker = Worker()
    
    scheduler.submit_task(task)
    worker.execute_task(scheduler.task_queue.popleft())
    
    assert task.get_state() == 'SUCCESS'

    with pytest.raises(ValueError):
        scheduler.submit_task(task)
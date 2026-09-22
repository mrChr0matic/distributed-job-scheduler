import pytest
import time
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

    assert task.get_state() == "PENDING"
    assert len(scheduler.task_queue) == 0
    
def test_submit_completed_task():
    task = Task(
        inputs={"a": 1, "b": 2},
        function="add"
    )
    scheduler = Scheduler()
    worker = Worker()
    
    scheduler.submit_task(task)
    scheduler.enqueue_ready_tasks()
    scheduler.run_all_tasks()
    
    assert task.get_state() == 'SUCCESS'

    with pytest.raises(ValueError):
        scheduler.submit_task(task)
        
def test_run_all_tasks():
    scheduler = Scheduler()
    assert scheduler.worker_count == 3
    
    task1 = Task(inputs={"a": 1, "b": 2}, function="add")
    task2 = Task(inputs={"a": 10, "b": 3}, function="sub")
    task3 = Task(inputs={"a": 5}, src_file="src/modules/echo.py")
    task4 = Task(inputs={"a": 10, "b": 30}, function="add")
    task5 = Task(inputs={"a": 10, "b": 30}, function="sub")
    

    scheduler.submit_task(task1)
    scheduler.submit_task(task2)
    scheduler.submit_task(task3)
    scheduler.submit_task(task4)
    scheduler.submit_task(task5)

    scheduler.run_all_tasks()

    assert task1.get_state() == "SUCCESS"
    assert task2.get_state() == "SUCCESS"
    assert task3.get_state() == "SUCCESS"
    assert task4.get_state() == "SUCCESS"
    assert task5.get_state() == "SUCCESS"
    

    assert task1.get_out() == 3
    assert task2.get_out() == 7
    assert task3.get_out() == {"a" : 5}
    assert task4.get_out() == 40
    assert task5.get_out() == -20

    assert len(scheduler.task_queue) == 0
    assert len(scheduler.busy_workers) == 0
    assert len(scheduler.worker_pool) == 3

def test_tasks_run_concurrently():
    scheduler = Scheduler(worker_count=3)

    tasks = [
        Task(
            inputs={"seconds": 0.2},
            src_file="src/modules/sleep.py"
        )
        for _ in range(3)
    ]

    for task in tasks:
        scheduler.submit_task(task)

    start = time.perf_counter()

    scheduler.run_all_tasks()

    elapsed = time.perf_counter() - start

    assert elapsed < 0.5

    for task in tasks:
        assert task.get_state() == "SUCCESS"

def test_tasks_run_concurrently():
    scheduler = Scheduler(worker_count=3)

    tasks = [
        Task(
            inputs={"seconds": 0.2},
            src_file="src/modules/sleep.py"
        )
        for _ in range(3)
    ]

    for task in tasks:
        scheduler.submit_task(task)

    start = time.perf_counter()

    scheduler.run_all_tasks()

    elapsed = time.perf_counter() - start

    assert elapsed < 0.5

    for task in tasks:
        assert task.get_state() == "SUCCESS"
        assert task.get_out() == 0.2

def test_workers_are_reused():
    scheduler = Scheduler(worker_count=3)

    tasks = [
        Task(inputs={"a": i, "b": 1}, function="add")
        for i in range(5)
    ]

    for task in tasks:
        scheduler.submit_task(task)

    scheduler.run_all_tasks()

    assert len(scheduler.task_queue) == 0
    assert len(scheduler.busy_workers) == 0
    assert len(scheduler.worker_pool) == 3

    for task in tasks:
        assert task.get_state() == "SUCCESS"
        
def test_failed_task_does_not_lose_worker():
    scheduler = Scheduler(worker_count=3)

    good_task1 = Task(
        inputs={"a": 1, "b": 2},
        function="add"
    )

    bad_task = Task(
        inputs={"a": 1},
        function="does_not_exist"
    )

    good_task2 = Task(
        inputs={"a": 10, "b": 20},
        function="add"
    )
    
    scheduler.submit_task(good_task1)
    scheduler.submit_task(bad_task)
    scheduler.submit_task(good_task2)

    scheduler.run_all_tasks()
    
    assert good_task1.get_state() == "SUCCESS"
    assert bad_task.get_state() == "FAILED"
    assert good_task2.get_state() == "SUCCESS"

    assert len(scheduler.worker_pool) == 3
    assert len(scheduler.busy_workers) == 0
    assert len(scheduler.task_queue) == 0

def test_run_all_tasks_empty():
    scheduler = Scheduler(worker_count=3)

    scheduler.run_all_tasks()

    assert len(scheduler.task_queue) == 0
    assert len(scheduler.busy_workers) == 0
    assert len(scheduler.worker_pool) == 3

def test_more_tasks_than_workers():
    scheduler = Scheduler(worker_count=3)

    tasks = [
        Task(inputs={"a": i, "b": 1}, function="add")
        for i in range(10)
    ]

    for task in tasks:
        scheduler.submit_task(task)

    scheduler.run_all_tasks()

    for task in tasks:
        assert task.get_state() == "SUCCESS"

    assert len(scheduler.task_queue) == 0
    assert len(scheduler.busy_workers) == 0
    assert len(scheduler.worker_pool) == 3
    
def test_scheduler_state():
    scheduler = Scheduler()
    tasks = [
        Task(inputs={"a": i, "b": 1}, function="add")
        for i in range(10)
    ]
    for task in tasks:
        scheduler.submit_task(task)
        
    assert scheduler.is_running() is False
    scheduler.run_all_tasks()
    assert scheduler.is_running() is False
    
def test_retry_exhausted():
    scheduler = Scheduler()

    task = Task(
        inputs={"a": 1},
        function="does_not_exist"
    )

    scheduler.submit_task(task)
    scheduler.run_all_tasks()

    assert task.retry_count == 2
    assert task.get_state() == "FAILED"
    
def test_scheduler_respects_dependencies():
    scheduler = Scheduler()

    task_a = Task(inputs={"a": 1, "b": 2}, function="add")
    task_b = Task(inputs={"a": 10, "b": 3}, function="sub")

    scheduler.submit_task(task_a)
    scheduler.submit_task(task_b)

    scheduler.set_task_dependency(task_a, task_b)

    ready = scheduler.get_ready_tasks()

    assert ready == [task_a]
    assert task_a.get_state() == "PENDING"
    assert task_b.get_state() == "PENDING"
    
def test_enqueue_ready_tasks():
    scheduler = Scheduler()

    task_a = Task(inputs={"a": 1, "b": 2}, function="add")
    task_b = Task(inputs={"a": 10, "b": 3}, function="sub")

    scheduler.submit_task(task_a)
    scheduler.submit_task(task_b)

    scheduler.set_task_dependency(task_a, task_b)

    scheduler.enqueue_ready_tasks()

    assert task_a.get_state() == "QUEUED"
    assert task_b.get_state() == "PENDING"
    assert list(scheduler.task_queue) == [task_a]
    
def test_run_tasks_with_dependency():
    scheduler = Scheduler()

    task_a = Task(inputs={"a": 1, "b": 2}, function="add")
    task_b = Task(inputs={"a": 10, "b": 3}, function="sub")

    scheduler.submit_task(task_a)
    scheduler.submit_task(task_b)

    scheduler.set_task_dependency(task_a, task_b)

    scheduler.run_all_tasks()

    assert task_a.get_state() == "SUCCESS"
    assert task_b.get_state() == "SUCCESS"
    assert task_a.task_out == 3
    assert task_b.task_out == 7
    
def test_one_task_unblocks_multiple_tasks():
    scheduler = Scheduler(worker_count=2)

    task_a = Task(inputs={"a": 1, "b": 2}, function="add")
    task_b = Task(inputs={"a": 10, "b": 3}, function="sub")
    task_c = Task(inputs={"a": 20, "b": 5}, function="sub")

    scheduler.submit_task(task_a)
    scheduler.submit_task(task_b)
    scheduler.submit_task(task_c)

    scheduler.set_task_dependency(task_a, task_b)
    scheduler.set_task_dependency(task_a, task_c)

    scheduler.run_all_tasks()

    assert task_a.get_state() == "SUCCESS"
    assert task_b.get_state() == "SUCCESS"
    assert task_c.get_state() == "SUCCESS"
    
def test_task_waits_for_all_dependencies():
    scheduler = Scheduler(worker_count=2)

    task_a = Task(inputs={"a": 1, "b": 2}, function="add")
    task_b = Task(inputs={"a": 10, "b": 3}, function="sub")
    task_d = Task(inputs={"a": 20, "b": 5}, function="sub")

    scheduler.submit_task(task_a)
    scheduler.submit_task(task_b)
    scheduler.submit_task(task_d)

    scheduler.set_task_dependency(task_a, task_d)
    scheduler.set_task_dependency(task_b, task_d)

    scheduler.run_all_tasks()

    assert task_a.get_state() == "SUCCESS"
    assert task_b.get_state() == "SUCCESS"
    assert task_d.get_state() == "SUCCESS"

def test_task_dependency_failure():
    scheduler = Scheduler(worker_count=2)

    task_a = Task(inputs={"a": 1, "b": 2}, function="add")
    task_b = Task(inputs={"a": 10, "b": 3}, function="invalid_function")
    task_d = Task(inputs={"a": 20, "b": 5}, function="sub")

    scheduler.submit_task(task_a)
    scheduler.submit_task(task_b)
    scheduler.submit_task(task_d)

    scheduler.set_task_dependency(task_a, task_d)
    scheduler.set_task_dependency(task_b, task_d)

    scheduler.run_all_tasks()

    assert task_a.get_state() == "SUCCESS"
    assert task_b.get_state() == "FAILED"
    assert task_d.get_state() == "PENDING"
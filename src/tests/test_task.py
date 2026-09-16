from base.task import Task
import pytest

def test_add_task():
    task = Task(
        inputs={"a" : 1, "b" : 2},
        function="add"   
    )
    
    assert task.state == "PENDING"
    task.execute_task()
    assert task.state == "SUCCESS"
    assert task.task_out == 3

def test_sub_task():
    task = Task(
        inputs={"a": 10, "b": 3, "c": 2},
        function="sub"
    )

    assert task.get_state() == "PENDING"

    task.execute_task()

    assert task.get_state() == "SUCCESS"
    assert task.get_out() == 5
    
def test_unknown_function():
    task = Task(
        inputs={"a": 10, "b": 3},
        function="multiply"
    )

    assert task.get_state() == "PENDING"

    with pytest.raises(ValueError):
        task.execute_task()

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
    
    task.execute_task()
    print(task.task_out)
    assert task.task_out == {"a": 10}
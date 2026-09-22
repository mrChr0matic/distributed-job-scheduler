import pytest
from base.dag import DAG


def test_add_task():
    dag = DAG()

    task_id = "task-1"
    dag.add_task(task_id)

    assert dag.graph == {
        "task-1": []
    }


def test_add_duplicate_task():
    dag = DAG()

    dag.add_task("task-1")
    dag.add_task("task-1")

    assert len(dag.graph) == 1


def test_add_dependency():
    dag = DAG()

    dag.add_edge("task-1", "task-2")

    assert dag.graph == {
        "task-1": ["task-2"],
        "task-2": []
    }


def test_dependency_cycle():
    dag = DAG()

    dag.add_edge("task-1", "task-2")

    with pytest.raises(ValueError):
        dag.add_edge("task-2", "task-1")
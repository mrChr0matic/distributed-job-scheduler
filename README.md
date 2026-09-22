# Distributed Job Scheduler

A Python-based distributed job scheduler inspired by systems like Airflow and Celery. This project is currently in the initial phases of development, focusing on building a robust local single-process scheduler with DAG support before scaling out to a fully distributed architecture.

## Project Goal
To build a production-grade distributed job scheduler from scratch with zero infrastructure cost (running locally). The architecture is being built incrementally, starting from a single-process queue up to a fully distributed, Dockerized system with PostgreSQL, Redis, FastAPI, and Observability tools.

## Work Done So Far
The project has currently implemented **Phase 1 (Single-Process Scheduler)**, incorporating advanced concepts like **Retries (Phase 7)** and **DAG-based workflows (Phase 8)** locally.

### Core Components Implemented:
- **Task Management (`src/base/task.py`)**: Representation of individual jobs with retry capabilities.
- **State Machine (`src/base/state_machine.py`)**: Tracks task lifecycle states (PENDING, QUEUED, RUNNING, SUCCESS, FAILED).
- **DAG / Workflows (`src/base/dag.py`)**: Directed Acyclic Graph implementation to define and evaluate task dependencies.
- **Workers (`src/base/worker.py`)**: Executes tasks safely.
- **Scheduler (`src/base/scheduler.py`)**: Central coordinator that:
  - Manages an in-memory task queue.
  - Spawns workers using a thread pool (`ThreadPoolExecutor`).
  - Evaluates DAGs to identify and enqueue ready tasks.
  - Re-queues tasks automatically if they fail and have remaining retries.
- **Job Modules (`src/modules/`)**: Example task scripts (echo, sleep, failure) for testing different scenarios.
- **Test Suite (`src/tests/`)**: Comprehensive unit tests using `pytest` for all base components.

## Next Steps
As outlined in the `distributed_job_scheduler_roadmap.md`, the next milestones are:
- **Phase 2 (FastAPI)**: Exposing the scheduler via a REST API to separate the client interface from the scheduler execution.
- **Phase 3 (PostgreSQL)**: Persisting job states, metadata, and results in a relational datasrc.base.
- **Phase 4 (Redis Queue)**: Replacing the in-memory queue with Redis to decouple job scheduling from job execution.
- **Future Phases**: Scaling to distributed workers, adding heartbeats, scheduling policies (priority, cron), and observability (Prometheus/Grafana).

## Development Setup

```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate

# Run the test suite
pytest src/tests/
```

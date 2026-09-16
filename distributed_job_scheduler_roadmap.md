# Distributed Job Scheduler — Project Roadmap

## Goal

Build a production-grade distributed job scheduler from scratch, inspired by systems such as Airflow/Celery, while keeping the entire project **₹0 cost** by running infrastructure locally.

Primary learning goals:

- Backend engineering
- Distributed systems
- Queues and workers
- Scheduling
- Reliability and fault tolerance
- Databases
- APIs
- Observability
- Docker
- System design
- Practical SDE interview preparation

This project is especially suited to a profile with Data Engineering experience in cloud platforms, Spark, and SQL because it deliberately strengthens backend/distributed-systems depth.

---

# Final Architecture

```text
                         USER
                           |
                           v
                    +-------------+
                    |   FastAPI   |
                    |     API     |
                    +------+------+
                           |
                           v
                    +-------------+
                    |  Scheduler  |
                    +------+------+
                           |
                           v
                    +-------------+
                    |    Redis    |
                    |    Queue    |
                    +------+------+
                           |
              +------------+------------+
              |            |            |
              v            v            v
          Worker 1     Worker 2     Worker 3
              |            |            |
              +------------+------------+
                           |
                           v
                    +-------------+
                    | PostgreSQL  |
                    | Job Metadata|
                    +-------------+
```

Later:

```text
Prometheus -> Grafana
Docker Compose -> Entire local platform
```

---

# Technology Stack

All core infrastructure should remain free and local.

- Python
- FastAPI
- PostgreSQL
- Redis
- Docker / Docker Compose
- Prometheus
- Grafana
- pytest
- GitHub / GitHub Actions

Do **not** use paid cloud infrastructure initially.

Do not use Airflow or Celery to implement the core scheduler. They may be studied for architectural inspiration, but the core functionality should be implemented ourselves.

---

# Build Philosophy

Do not build the entire architecture at once.

Progressively increase complexity:

```text
Single process
    ↓
FastAPI
    ↓
PostgreSQL
    ↓
Redis
    ↓
Multiple workers
    ↓
Heartbeats
    ↓
Retries
    ↓
DAGs
    ↓
Scheduling
    ↓
Concurrency / Priority
    ↓
Observability
    ↓
Docker
    ↓
Failure testing
    ↓
Production-grade system
```

The next phase should generally be started only after the previous phase works.

The goal is to encounter real engineering problems naturally rather than prematurely designing a huge system.

---

# Phase 0 — Understand the Problem

The basic purpose:

> A user submits a task, the system schedules it, a worker executes it, and the system records the result.

Basic lifecycle:

```text
Receive task
    ↓
Store task
    ↓
Queue task
    ↓
Worker picks task
    ↓
Execute
    ↓
Report result
    ↓
Store status
```

Core task states:

```text
PENDING
   ↓
RUNNING
   ↓
SUCCESS

or

PENDING
   ↓
RUNNING
   ↓
FAILED
```

---

# Phase 1 — Single-Process Scheduler

### Infrastructure

None.

No Redis.
No PostgreSQL.
No Docker.

Use only Python.

Build:

```text
Client
  ↓
Scheduler
  ↓
In-memory Queue
  ↓
Worker
  ↓
Result
```

Example conceptual API:

```python
submit("python script.py")
```

Implement:

- Task creation
- In-memory queue
- Worker
- Task execution
- Task status
- Result storage
- Failure handling

### Goal

Understand the task lifecycle before introducing distributed components.

---

# Phase 2 — FastAPI

Expose the scheduler through an API.

Endpoints:

```text
POST /jobs
GET  /jobs
GET  /jobs/{job_id}
POST /jobs/{job_id}/cancel
```

Example:

```http
POST /jobs
```

Request:

```json
{
  "command": "python process.py"
}
```

Response:

```json
{
  "job_id": "abc123",
  "status": "PENDING"
}
```

Query:

```http
GET /jobs/abc123
```

Response:

```json
{
  "job_id": "abc123",
  "status": "RUNNING"
}
```

### Goal

Separate:

```text
API Layer
    ↓
Scheduler
    ↓
Worker
```

---

# Phase 3 — PostgreSQL

Move persistent job state from memory to PostgreSQL.

Possible table:

```text
jobs
--------------------------------
id
command
status
created_at
started_at
finished_at
worker_id
result
error
retry_count
```

The system should survive application restarts.

Important distinction:

```text
Application state
        vs
Persistent system state
```

### Goal

Learn how a distributed service manages durable state.

---

# Phase 4 — Redis Queue

Separate job metadata from job execution.

PostgreSQL answers:

> What jobs exist and what is their state?

Redis answers:

> Which jobs need to be executed?

Architecture:

```text
                    API
                     |
             +-------+-------+
             |               |
             v               v
        PostgreSQL         Redis
        Job State          Queue
                             |
                             v
                          Worker
```

Flow:

```text
POST /jobs
    ↓
Create DB record
    ↓
PENDING
    ↓
Push job ID to Redis
    ↓
Worker pops job
    ↓
RUNNING
    ↓
Execute
    ↓
SUCCESS / FAILED
    ↓
Update PostgreSQL
```

### Goal

Understand queue-based architectures.

---

# Phase 5 — Multiple Workers

Run multiple workers:

```text
Worker 1
Worker 2
Worker 3
```

All consume from Redis.

Example:

```text
Job 1 -> Worker 1
Job 2 -> Worker 2
Job 3 -> Worker 3
Job 4 -> Worker 1
Job 5 -> Worker 2
```

Questions to start investigating:

- How are jobs distributed?
- What happens when a worker dies?
- Can two workers execute the same task?
- What happens if a worker disappears after taking a task?
- How do we identify workers?

### Goal

Move from a local scheduler to an actual distributed worker architecture.

---

# Phase 6 — Worker Heartbeats

Workers periodically report:

```text
Worker 1: alive
Worker 2: alive
Worker 3: alive
```

Example:

```text
Worker 2
heartbeat
heartbeat
heartbeat
DEAD
```

Scheduler detects:

```text
last heartbeat > timeout
```

and marks:

```text
Worker 2 = DEAD
```

Then solve:

> What happens to the task Worker 2 was executing?

This should lead naturally to task recovery.

### Goal

Understand liveness detection and failure recovery.

---

# Phase 7 — Retries

Failed tasks should be retried.

Example:

```text
Job A
 ↓
Worker 1
 ↓
FAILED
 ↓
Retry #1
 ↓
Worker 2
 ↓
FAILED
 ↓
Retry #2
 ↓
Worker 3
 ↓
SUCCESS
```

Implement:

```text
max_retries
retry_count
retry_delay
```

Then exponential backoff:

```text
1 sec
2 sec
4 sec
8 sec
16 sec
```

Questions:

- Which failures are retryable?
- How do we avoid infinite retries?
- What happens after max retries?
- How do we prevent duplicate execution?

### Goal

Learn reliable task execution.

---

# Phase 8 — DAGs

Move from individual jobs to workflows.

Example:

```text
        A
       /       B   C
       \ /
        D
```

Meaning:

```text
A must finish
    ↓
B and C can run
    ↓
D waits for both
```

The scheduler must determine:

> Which tasks are ready to execute?

Useful concepts:

- Directed Acyclic Graphs
- Dependencies
- Topological ordering
- Ready queues
- Dependency state

### Goal

Build workflow orchestration.

---

# Phase 9 — Scheduling

Support execution at a specified time.

Examples:

```text
Run immediately
Run at 02:00
Run every day
Run every 5 minutes
```

Flow:

```text
Scheduled Job
      ↓
Scheduler
      ↓
Execution time reached?
      ↓
     YES
      ↓
    Redis
      ↓
   Worker
```

Eventually support cron-style expressions.

### Goal

Separate:

```text
When should a task run?
```

from:

```text
How should a task run?
```

---

# Phase 10 — Priority and Concurrency

Imagine:

```text
1,000 jobs
10 workers
```

You need policies for:

- Maximum concurrent jobs
- Worker concurrency
- Queue limits
- Job priority
- Per-user limits
- High-priority jobs
- Fairness

Example:

```text
Priority 10 -> execute first
Priority 5  -> execute next
Priority 1  -> execute later
```

Questions:

- What if one user submits 500 jobs?
- Can one user starve everyone else?
- How do high-priority jobs jump the queue?
- How many jobs can a worker execute simultaneously?

### Goal

Understand scheduling policies and resource management.

---

# Phase 11 — Observability

Add:

```text
Prometheus
    ↓
Grafana
```

Track:

```text
Jobs submitted
Jobs completed
Jobs failed
Job latency
Queue length
Worker utilization
Retry count
Worker failures
Task execution duration
```

Example dashboard:

```text
+----------------------------------+
| Jobs Running              17    |
| Jobs Completed         12,482    |
| Jobs Failed               143    |
| Queue Length               28    |
| Active Workers              8    |
+----------------------------------+
```

### Goal

Make the system observable rather than merely functional.

---

# Phase 12 — Dockerize Everything

Create a Docker Compose environment containing:

```text
api
scheduler
worker-1
worker-2
postgres
redis
prometheus
grafana
```

Target:

```bash
docker compose up
```

should start the entire system.

### Goal

Make the project reproducible and easy to run.

---

# Phase 13 — Break It Deliberately

This is a critical phase.

Do not stop when the happy path works.

Test:

```text
Kill a worker
Kill the scheduler
Restart Redis
Restart PostgreSQL
Submit 10,000 jobs
Submit duplicate jobs
Run a task for 10 minutes
Force a task to crash
Make workers disappear
Restart the entire system
```

For every failure, ask:

```text
What happened?
Why did it happen?
What should have happened?
How can the architecture guarantee that behavior?
```

### Goal

Turn the project from a demo into an engineering system.

---

# Important Distributed-System Questions

As the project grows, actively investigate these:

### Task execution semantics

- At-most-once?
- At-least-once?
- Exactly-once?

Understand why exactly-once execution is difficult in distributed systems.

### Duplicate execution

What if:

```text
Worker executes task
      ↓
Worker crashes before reporting SUCCESS
      ↓
Scheduler assumes task failed
      ↓
Task gets executed again
```

How should the system handle this?

### Scheduler failure

What happens if:

```text
Scheduler
   ↓
CRASH
```

Who takes over?

### Worker failure

What happens if:

```text
Worker
   ↓
takes task
   ↓
dies
```

How is the task recovered?

### Queue failure

What happens if Redis goes down?

### Database failure

What happens if PostgreSQL becomes unavailable while workers are executing tasks?

These questions are where much of the real learning happens.

---

# Suggested Repository Structure

Start simple and evolve it.

```text
distributed-job-scheduler/
│
├── api/
│   ├── routes/
│   └── schemas/
│
├── scheduler/
│
├── worker/
│
├── queue/
│
├── database/
│
├── models/
│
├── tests/
│
├── scripts/
│
├── docker/
│
├── monitoring/
│
├── docs/
│
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .gitignore
```

Do not obsess over the final folder structure early.

Refactor as the architecture evolves.

---

# Development Rule

At every phase:

```text
1. Understand the requirement
2. Design the smallest solution
3. Implement
4. Test
5. Break it
6. Fix it
7. Document what you learned
8. Move to the next phase
```

Avoid copying a complete implementation from a tutorial.

Use documentation and references when necessary, but solve the architectural problems yourself.

---

# What NOT to Do Initially

Do not start with:

- Kubernetes
- AWS
- Azure
- GCP
- Kafka
- Microservices everywhere
- Kubernetes operators
- Complex UI
- Machine learning
- AI features

Those can come later if they solve a real requirement.

The initial system should be:

```text
Python
+
FastAPI
+
PostgreSQL
+
Redis
```

running locally.

---

# Final Target

The finished project should demonstrate:

```text
Backend Engineering
        +
Distributed Systems
        +
Database Design
        +
Queueing
        +
Scheduling
        +
Fault Tolerance
        +
Concurrency
        +
Observability
        +
Docker
        +
Testing
        +
System Design
```

This should become a flagship portfolio/interview project rather than a collection of disconnected features.

---

# Current Starting Point

## Phase 1 — Single-Process Scheduler

Start here.

### First milestone

Build:

```text
submit task
    ↓
queue
    ↓
worker
    ↓
execute
    ↓
store result
    ↓
return status
```

No database.
No Redis.
No Docker.

Once this works, proceed to FastAPI.

---

# How to Continue This Project in a New Chat

Paste this document into the new conversation and say:

> "Continue the Distributed Job Scheduler project from this roadmap. We are currently at Phase X. Act as my technical mentor. Don't jump ahead unnecessarily. Help me reason through the architecture and implementation rather than simply giving me the finished code."

Keep updating the **Current Starting Point** section as the project progresses.

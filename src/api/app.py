from fastapi import FastAPI, HTTPException
from uuid import UUID
from src.base.task import Task
from src.base.scheduler import Scheduler
from src.api.schemas import TaskRequest

app = FastAPI()
scheduler = Scheduler()
    
@app.get("/health")
def health():
    return {'status' : 'ok'}


@app.post("/jobs", status_code=201)
def set_task(task_info : TaskRequest):
    task = Task(inputs=task_info.inputs, function=task_info.function, src_file=task_info.src_file)
    scheduler.submit_task(task)
    return {
        "task_id" : task.task_id,
        "state" : task.get_state()
    }
    
@app.get("/jobs")
def get_jobs():
    jobs = []
    for task_id in scheduler.task_directory:
        jobs.append({"task_id" : str(task_id), "state" : scheduler.task_directory[task_id].get_state()})
    return jobs

@app.get("/jobs/{job_id}")
def get_job_with_id(job_id : UUID):
    if job_id not in scheduler.task_directory:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "task_id" : job_id,
        "state" : scheduler.task_directory[job_id].get_state()
    }
    
@app.post("/jobs/{job_id}/cancel")
def cancel_job_with_id(job_id : UUID):
    if job_id not in scheduler.task_directory:
        raise HTTPException(status_code=404, detail="Job not found")
    scheduler.cancel_task(job_id)
    return {
        "task_id" : job_id,
        "state" : scheduler.task_directory[job_id].get_state() 
    }
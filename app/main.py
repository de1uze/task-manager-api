import logging

from fastapi import FastAPI, HTTPException, status

from app.config import settings
from app.errors import register_exception_handlers
from app.logging_setup import configure_logging
from app.middleware import RequestContextMiddleware
from app.models import Task, TaskCreate, TaskUpdate
from app.store import store

configure_logging()
logger = logging.getLogger("task-manager")

app = FastAPI(title=settings.app_name)
app.add_middleware(RequestContextMiddleware)
register_exception_handlers(app)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to the Task Manager API"}


@app.get("/health")
def health() -> dict[str, str]:
    logger.debug("health check")
    return {"status": "ok"}


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    return store.list()


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    task = store.create(payload)
    logger.info("task created id=%d title=%r", task.id, task.title)
    return task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"task {task_id} not found")
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate) -> Task:
    task = store.update(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail=f"task {task_id} not found")
    logger.info("task updated id=%d", task_id)
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> None:
    if not store.delete(task_id):
        raise HTTPException(status_code=404, detail=f"task {task_id} not found")
    logger.info("task deleted id=%d", task_id)

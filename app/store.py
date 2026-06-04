from threading import Lock

from app.models import Task, TaskCreate, TaskUpdate


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1
        self._lock = Lock()

    def list(self) -> list[Task]:
        with self._lock:
            return list(self._tasks.values())

    def get(self, task_id: int) -> Task | None:
        with self._lock:
            return self._tasks.get(task_id)

    def create(self, data: TaskCreate) -> Task:
        with self._lock:
            task = Task(id=self._next_id, **data.model_dump())
            self._tasks[task.id] = task
            self._next_id += 1
            return task

    def update(self, task_id: int, data: TaskUpdate) -> Task | None:
        with self._lock:
            current = self._tasks.get(task_id)
            if current is None:
                return None
            updated = current.model_copy(
                update={k: v for k, v in data.model_dump().items() if v is not None}
            )
            self._tasks[task_id] = updated
            return updated

    def delete(self, task_id: int) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None


store = TaskStore()

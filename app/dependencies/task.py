from core.database import get_db
from fastapi import Depends
from repositories import TaskRepository
from services.task_service import TaskService
from sqlalchemy.orm import Session


def get_task_service(
    db: Session = Depends(get_db),
) -> TaskService:
    task_repo = TaskRepository(db)
    return TaskService(task_repo)

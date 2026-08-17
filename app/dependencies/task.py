from sqlalchemy.orm import Session
from fastapi import Depends
from core.database import get_db
from services.task_service import TaskService
from repositories import TaskRepository



def get_task_service(
    db: Session = Depends(get_db),
) -> TaskService:
    task_repo = TaskRepository(db)
    return TaskService(task_repo)

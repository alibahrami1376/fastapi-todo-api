from datetime import datetime,timezone

from sqlalchemy.orm import Session

from models import TaskModel, PriorityTypes


class TaskRepository:
    """Repository class for managing task-related database operations."""
    
    def __init__(self, db: Session):
        self.db = db

    def _base_query(self):
        return self.db.query(TaskModel).filter(
            TaskModel.deleted_at.is_(None)
        )

    def get_by_id(self, task_id: int)-> TaskModel | None:
        return (
            self._base_query()
            .filter(TaskModel.id == task_id)
            .first()
        )

    
    def get_by_id_and_owner_id(self, task_id: int, owner_id: int)-> TaskModel | None:
        return (
            self._base_query()
            .filter(
                TaskModel.id == task_id,
                TaskModel.owner_id == owner_id,
            )
            .first()
        )


    def get_by_owner_id(self, owner_id: int):
        return (
            self._base_query()
            .filter(TaskModel.owner_id == owner_id)
            .all()
        )
    
    def create_task(
        self,
        title: str,
        description: str | None,
        priority: PriorityTypes,
        due_date: datetime | None,
        owner_id: int,
    ) -> TaskModel:
        task = TaskModel(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            owner_id=owner_id,
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task
    
    def update_task(self,task : TaskModel) -> TaskModel:
       
        self.db.commit()
        self.db.refresh(task)
        
        return task

    def delete_task(self, task: TaskModel) -> None:
        task.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(task)
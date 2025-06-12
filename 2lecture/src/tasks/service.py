"""
Task service layer containing business logic for task operations.
"""
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from tasks.crud import TaskDAO
from tasks.exceptions import TaskValidationException
from tasks.models import TaskCreate, TaskUpdate
from tasks.schema import Task as DBTask


class TaskService:

    @staticmethod
    async def get_all_tasks(db: AsyncSession) -> List[DBTask]:
        """Get all tasks."""
        return await TaskDAO.get_all_tasks(db)

    @staticmethod
    async def get_task_by_id(task_id: int, db: AsyncSession) -> DBTask:
        """Get task by ID."""
        return await TaskDAO.get_task_by_id_or_raise(task_id, db)

    @staticmethod
    async def create_task(task_data: TaskCreate, db: AsyncSession) -> DBTask:
        """Create a new task."""
        if not task_data.title or len(task_data.title.strip()) == 0:
            raise TaskValidationException("Title cannot be empty")

        new_task = DBTask(
            title=task_data.title.strip(),
            description=task_data.description,
            completed=task_data.completed
        )

        return await TaskDAO.create_task(new_task, db)

    @staticmethod
    async def update_task(
        task_id: int, 
        task_data: TaskUpdate, 
        db: AsyncSession
    ) -> DBTask:
        """Update an existing task."""
        task = await TaskDAO.get_task_by_id_or_raise(task_id, db)

        # Update only provided fields
        if task_data.title is not None:
            if len(task_data.title.strip()) == 0:
                raise TaskValidationException("Title cannot be empty")
            task.title = task_data.title.strip()

        if task_data.description is not None:
            task.description = task_data.description

        if task_data.completed is not None:
            task.completed = task_data.completed

        return await TaskDAO.update_task(task, db)

    @staticmethod
    async def delete_task(task_id: int, db: AsyncSession) -> bool:
        """Delete a task."""
        task = await TaskDAO.get_task_by_id_or_raise(task_id, db)
        return await TaskDAO.delete_task(task, db) 
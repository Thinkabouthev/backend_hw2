from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from tasks.exceptions import DatabaseException, TaskNotFoundException
from tasks.schema import Task


class TaskDAO:

    @staticmethod
    async def get_all_tasks(db: AsyncSession) -> List[Task]:
        """Get all tasks."""
        try:
            query = select(Task)
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise DatabaseException(f"get_all_tasks: {str(e)}")

    @staticmethod
    async def get_task_by_id(task_id: int, db: AsyncSession) -> Optional[Task]:
        """Get task by ID."""
        try:
            query = select(Task).where(Task.id == task_id)
            result = await db.execute(query)
            return result.scalars().first()
        except Exception as e:
            raise DatabaseException(f"get_task_by_id: {str(e)}")

    @staticmethod
    async def create_task(task: Task, db: AsyncSession) -> Task:
        """Create a new task."""
        try:
            db.add(task)
            await db.commit()
            await db.refresh(task)
            return task
        except IntegrityError as e:
            await db.rollback()
            raise DatabaseException(f"create_task (integrity): {str(e)}")
        except Exception as e:
            await db.rollback()
            raise DatabaseException(f"create_task: {str(e)}")

    @staticmethod
    async def update_task(task: Task, db: AsyncSession) -> Task:
        """Update an existing task."""
        try:
            await db.commit()
            await db.refresh(task)
            return task
        except Exception as e:
            await db.rollback()
            raise DatabaseException(f"update_task: {str(e)}")

    @staticmethod
    async def delete_task(task: Task, db: AsyncSession) -> bool:
        """Delete a task."""
        try:
            await db.delete(task)
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            raise DatabaseException(f"delete_task: {str(e)}")

    @staticmethod
    async def get_task_by_id_or_raise(task_id: int, db: AsyncSession) -> Task:
        """Get task by ID or raise TaskNotFoundException."""
        task = await TaskDAO.get_task_by_id(task_id, db)
        if task is None:
            raise TaskNotFoundException(task_id)
        return task

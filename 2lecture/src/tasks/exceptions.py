"""
Custom exceptions for the tasks module.
"""
from fastapi import HTTPException, status


class TaskException(Exception):
    """Base exception for task-related errors."""
    pass


class TaskNotFoundException(TaskException):
    """Raised when a task is not found."""
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")


class TaskValidationException(TaskException):
    """Raised when task validation fails."""
    def __init__(self, message: str):
        super().__init__(f"Task validation error: {message}")


class DatabaseException(TaskException):
    """Raised when database operations fail."""
    def __init__(self, operation: str):
        self.operation = operation
        super().__init__(f"Database operation failed: {operation}")


def raise_http_exception(exception: TaskException) -> HTTPException:
    """Convert custom task exceptions to FastAPI HTTPExceptions."""
    if isinstance(exception, TaskNotFoundException):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exception)
        )
    elif isinstance(exception, TaskValidationException):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exception)
        )
    elif isinstance(exception, DatabaseException):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        ) 
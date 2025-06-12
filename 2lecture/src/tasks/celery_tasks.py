from datetime import datetime
from sqlalchemy import text
from database import SessionLocal
from tasks.schema import Task
from celery_worker import celery

@celery.task
def process_task_async(task_id: int):
    """Process a task asynchronously"""
    db = SessionLocal()
    try:
        # Find the task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return {"status": "error", "message": f"Task {task_id} not found"}
        
        # Simulate some processing
        task.description = f"{task.description}\nProcessed at {datetime.now()}"
        task.completed = True
        
        db.commit()
        return {"status": "success", "task_id": task_id}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@celery.task
def cleanup_completed_tasks():
    """Clean up old completed tasks"""
    db = SessionLocal()
    try:
        # Delete tasks that are completed and older than 30 days
        result = db.execute(
            text("""
                DELETE FROM tasks 
                WHERE completed = true 
                AND created_at < NOW() - INTERVAL '30 days'
                RETURNING id
            """)
        )
        deleted_ids = [row[0] for row in result]
        db.commit()
        return {
            "status": "success", 
            "deleted_count": len(deleted_ids),
            "deleted_ids": deleted_ids
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@celery.task
def send_task_notification(task_id: int):
    """Send a notification about a task (simulated)"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return {"status": "error", "message": f"Task {task_id} not found"}
            
        # Simulate sending notification
        notification = {
            "task_id": task.id,
            "title": task.title,
            "status": "completed" if task.completed else "pending",
            "timestamp": datetime.now().isoformat()
        }
        
        # In real application, you would send this to a notification service
        return {
            "status": "success",
            "notification_sent": notification
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close() 
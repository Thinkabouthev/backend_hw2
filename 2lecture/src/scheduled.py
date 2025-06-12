from celery import shared_task
import requests
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal
from tasks.crud import TaskDAO
from tasks.schema import Task

@shared_task
def fetch_data_from_website():
    try:
        # Using JSONPlaceholder - a free fake API for testing
        response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
        response.raise_for_status()
        data = response.json()
        
        # Create database session
        db = SessionLocal()
        try:
            # Create new task with data from the API
            new_task = Task(
                title=data.get('title', 'No Title'),
                description=data.get('body', 'No Description')  # 'body' is the field name in JSONPlaceholder API
            )
            db.add(new_task)
            db.commit()
            db.refresh(new_task)
            
            return {
                "status": "success", 
                "task_id": new_task.id,
                "data_fetched": data
            }
        except Exception as db_error:
            db.rollback()
            return {"status": "error", "message": f"Database error: {str(db_error)}"}
        finally:
            db.close()
    except requests.RequestException as req_error:
        return {"status": "error", "message": f"Request error: {str(req_error)}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}
from celery import Celery
from config import settings
import scheduled

celery = Celery(
    'tasks',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=['tasks.celery_tasks', 'scheduled']
)

# Optional configuration
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Task registration
@celery.task
def fetch_data_from_website():
    # Task code will be in scheduled.py
    pass

# Beat schedule configuration
celery.conf.beat_schedule = {
    # Daily data fetch at midnight
    'fetch_data_from_website': {
        'task': 'tasks.scheduled.fetch_data_from_website',
        'schedule': 3600.0,  # every hour
    },
    
    # Cleanup completed tasks every Sunday at 1 AM
    'cleanup_old_tasks': {
        'task': 'tasks.celery_tasks.cleanup_completed_tasks',
        'schedule': 86400.0,  # every day
    },
    
    # Process pending tasks every hour
    'process_pending_tasks': {
        'task': 'tasks.celery_tasks.process_task_async',
        'schedule': 3600.0,  # every hour
    }
}

if __name__ == '__main__':
    celery.start()
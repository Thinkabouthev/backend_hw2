from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List

from . import crud, models, schemas, auth
from .database import engine, SessionLocal
from .auth import get_current_user

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Management API",
    description="""
    A Task Management API with the following features:
    * User registration and authentication with JWT tokens
    * Create, read, update, and delete tasks
    * PostgreSQL database integration
    * Secure endpoints
    
    ## Authentication
    1. First, register a new user using the `/register` endpoint
    2. Then, get your access token using the `/token` endpoint
    3. Finally, click the 'Authorize' button and enter your token as: `Bearer your_token_here`
    """,
    version="1.0.0",
    openapi_tags=[
        {"name": "Authentication", "description": "Operations for user authentication"},
        {"name": "Tasks", "description": "Operations with tasks"},
        {"name": "Users", "description": "Operations with user data"}
    ]
)

# Security scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Task Management API",
        "documentation": "/docs",
        "endpoints": {
            "auth": [
                {"path": "/register", "method": "POST", "description": "Register a new user"},
                {"path": "/token", "method": "POST", "description": "Login and get access token"}
            ],
            "tasks": [
                {"path": "/tasks", "method": "GET", "description": "List all tasks"},
                {"path": "/tasks", "method": "POST", "description": "Create a new task"},
                {"path": "/tasks/{task_id}", "method": "GET", "description": "Get a specific task"},
                {"path": "/tasks/{task_id}", "method": "PUT", "description": "Update a task"},
                {"path": "/tasks/{task_id}", "method": "DELETE", "description": "Delete a task"}
            ],
            "user": [
                {"path": "/me", "method": "GET", "description": "Get current user info"}
            ]
        }
    }

@app.post("/register", response_model=schemas.User, tags=["Authentication"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with email and password
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(form_data: auth.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Get access token. Use the token in the 'Authorize' button as: Bearer your_token_here
    
    - **username**: Your registered email
    - **password**: Your password
    """
    return auth.login_for_access_token(form_data, db)

@app.get("/me", response_model=schemas.User, tags=["Users"])
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Get information about the current logged-in user
    """
    return current_user

@app.post("/tasks", response_model=schemas.Task, tags=["Tasks"])
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new task for the current user
    """
    return crud.create_task(db=db, task=task, user_id=current_user.id)

@app.get("/tasks", response_model=List[schemas.Task], tags=["Tasks"])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all tasks for the current user
    """
    tasks = crud.get_user_tasks(db, user_id=current_user.id, skip=skip, limit=limit)
    return tasks

@app.get("/tasks/{task_id}", response_model=schemas.Task, tags=["Tasks"])
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get a specific task by ID
    """
    task = crud.get_task(db, task_id=task_id)
    if task is None or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=schemas.Task, tags=["Tasks"])
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update a task by ID
    """
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None or db_task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.update_task(db=db, task_id=task_id, task=task)

@app.delete("/tasks/{task_id}", tags=["Tasks"])
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a task by ID
    """
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None or db_task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.delete_task(db=db, task_id=task_id)
    return {"message": "Task deleted successfully"} 
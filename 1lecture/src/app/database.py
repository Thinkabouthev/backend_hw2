from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import time
from sqlalchemy.exc import OperationalError

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "taskdb")

# Add timezone and other connection parameters
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}?options=-c%20timezone=UTC"

# Try to connect to the database with retries
max_retries = 5
retry_delay = 5  # seconds

for retry in range(max_retries):
    try:
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"options": "-c timezone=UTC"}
        )
        # Test the connection
        with engine.connect() as connection:
            break
    except OperationalError as e:
        if retry < max_retries - 1:
            print(f"Database connection failed. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("Failed to connect to the database after multiple retries")
            raise e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
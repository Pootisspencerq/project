from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .models import Base  # Ensure this import is correct for your models

SQLALCHEMY_DATABASE_URL = "sqlite:///./library.db"  # Adjust the DB URL if needed

# Create an engine that connects to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session factory bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the Base class (this will be used to define your models)
Base = Base

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/document_processor")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for SQLAlchemy models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    """
    Get database session dependency
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
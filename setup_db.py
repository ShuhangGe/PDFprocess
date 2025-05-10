#!/usr/bin/env python3
"""
Database setup script for Document Processing application

This script creates the PostgreSQL database and initializes the tables
based on the SQLAlchemy models defined in the application.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv

# Add the current directory to sys.path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import application modules
from app.db.database import engine, Base
from app.models.models import Document, LineItem, ProductCatalog, ProductMatch

# Load environment variables
load_dotenv()

def setup_database():
    """
    Set up database and tables for the application
    """
    # Get database URL from environment variable
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set.")
        print("Please create a .env file with DATABASE_URL=postgresql://username:password@localhost:5432/database_name")
        sys.exit(1)
    
    try:
        # Extract database name and connection info from the URL
        db_parts = database_url.split("/")
        db_name = db_parts[-1]
        connection_string = "/".join(db_parts[:-1])
        
        print(f"Setting up database: {db_name}")
        
        # Check if database exists, if not create it
        if not database_exists(database_url):
            print(f"Creating database '{db_name}'...")
            create_database(database_url)
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' already exists.")
        
        # Use SQLAlchemy to create all tables defined in the models
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
        
        print("\nDatabase setup completed successfully!")
        print("\nYou can now run the application using:")
        print("python run.py")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database() 
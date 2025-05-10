#!/usr/bin/env python3
"""
Database migration script to add missing columns to tables
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Add the current directory to sys.path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Load environment variables
load_dotenv()

def run_migration():
    """
    Run database migrations to add missing columns
    """
    # Get database URL from environment variable
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set.")
        print("Please create a .env file with DATABASE_URL=postgresql://username:password@localhost:5432/database_name")
        sys.exit(1)
    
    try:
        # Connect to the database
        print("Connecting to database...")
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Check if score column exists in product_matches
        print("Checking if 'score' column exists in 'product_matches' table...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'product_matches' AND column_name = 'score';
        """)
        
        if cursor.fetchone() is None:
            print("Adding 'score' column to 'product_matches' table...")
            cursor.execute("""
                ALTER TABLE product_matches 
                ADD COLUMN score FLOAT;
            """)
            print("Column 'score' added successfully!")
        else:
            print("Column 'score' already exists, no migration needed.")
        
        # Check if type column exists in product_catalog
        print("Checking if 'type' column exists in 'product_catalog' table...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'product_catalog' AND column_name = 'type';
        """)
        
        if cursor.fetchone() is None:
            print("Adding 'type' column to 'product_catalog' table...")
            cursor.execute("""
                ALTER TABLE product_catalog 
                ADD COLUMN type VARCHAR(255);
            """)
            print("Column 'type' added successfully!")
        else:
            print("Column 'type' already exists, no migration needed.")
        
        # Check if other needed columns exist in product_catalog
        required_columns = [
            "material", "size", "length", "coating", "thread_type"
        ]
        
        for column in required_columns:
            print(f"Checking if '{column}' column exists in 'product_catalog' table...")
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'product_catalog' AND column_name = '{column}';
            """)
            
            if cursor.fetchone() is None:
                print(f"Adding '{column}' column to 'product_catalog' table...")
                cursor.execute(f"""
                    ALTER TABLE product_catalog 
                    ADD COLUMN {column} VARCHAR(255);
                """)
                print(f"Column '{column}' added successfully!")
            else:
                print(f"Column '{column}' already exists, no migration needed.")
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error in migration: {e}")
        # Rollback changes if an error occurs
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)
    finally:
        # Close database connection
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration() 
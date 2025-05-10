#!/usr/bin/env python3
"""
Run script for Document Processing application

This script starts the FastAPI application using uvicorn.
"""

import os
import uvicorn
import sys
from dotenv import load_dotenv

# Make sure the current directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("Starting Document Processing Application...")
    print("Access the web interface at http://localhost:8000")
    print("API documentation available at http://localhost:8000/docs")
    print("\nPress CTRL+C to stop the server")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 
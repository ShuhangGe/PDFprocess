#!/usr/bin/env python3
"""
Setup script for Document Processing application

This script guides users through setting up the application without Docker.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current Python version: {current_version[0]}.{current_version[1]}")
        sys.exit(1)
    
    return True

def setup_virtual_environment():
    """Set up a virtual environment"""
    print("\nSetting up virtual environment...")
    
    # Check if venv already exists
    if os.path.exists("venv"):
        print("Virtual environment already exists.")
        return True
    
    # Create virtual environment
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Virtual environment created successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to create virtual environment.")
        sys.exit(1)

def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    
    # Determine the virtual environment's Python executable
    if platform.system() == "Windows":
        venv_python = os.path.join("venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join("venv", "bin", "python")
    
    # Upgrade pip
    try:
        subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    except subprocess.CalledProcessError:
        print("Warning: Failed to upgrade pip.")
    
    # Install dependencies
    try:
        subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies.")
        sys.exit(1)

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("\nChecking for .env file...")
    
    if os.path.exists(".env"):
        print(".env file already exists.")
        return True
    
    print("Creating .env file...")
    
    default_content = [
        "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/document_processing",
        "EXTRACTION_API_URL=https://plankton-app-qajlk.ondigitalocean.app",
        "MATCHING_API_URL=https://endeavor-interview-api-gzwki.ondigitalocean.app"
    ]
    
    try:
        with open(".env", "w") as f:
            f.write("\n".join(default_content))
        
        print(".env file created with default values.")
        print("Please edit this file if you need to change database credentials.")
        return True
    except Exception as e:
        print(f"Error: Failed to create .env file: {e}")
        sys.exit(1)

def setup_database():
    """Set up the database"""
    print("\nSetting up database...")
    
    # Determine the virtual environment's Python executable
    if platform.system() == "Windows":
        venv_python = os.path.join("venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join("venv", "bin", "python")
    
    # Run setup_db.py
    try:
        subprocess.run([venv_python, "setup_db.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to set up database.")
        print("Please ensure PostgreSQL is installed and running, and the DATABASE_URL in .env is correct.")
        print("You can manually set up the database later by running: python setup_db.py")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("Document Processing Application Setup")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Set up virtual environment
    setup_virtual_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Create .env file
    create_env_file()
    
    # Set up database
    db_setup_success = setup_database()
    
    print("\n" + "=" * 60)
    if db_setup_success:
        print("Setup completed successfully!")
    else:
        print("Setup completed with warnings.")
        print("Please check the output above for any issues.")
    
    # Print next steps
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("2. Run the application:")
    print("   python run.py")
    
    print("\n3. Access the application in your browser:")
    print("   http://localhost:8000")
    
    print("\n4. Import the product catalog by clicking the 'Import Catalog' button in the application.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 
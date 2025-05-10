# Quick Start Guide

This guide provides simple steps to set up and run the Document Processing application without Docker.

## Prerequisites

1. **Python 3.8+**: Make sure you have Python 3.8 or higher installed.
2. **PostgreSQL**: Install PostgreSQL on your machine if not already installed.

## Easy Setup (Recommended)

The easiest way to set up the project is using our setup script:

```bash
python setup.py
```

This script will:
- Create a virtual environment
- Install dependencies
- Set up the .env file
- Create the database and tables

After running the setup script, follow the instructions displayed at the end.

## Manual Setup

If you prefer to set up manually, follow these steps:

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate the virtual environment

On Windows:
```bash
venv\Scripts\activate
```

On macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL database

Create a database in PostgreSQL:
```bash
createdb document_processing
```

### 5. Configure environment variables

Create a `.env` file with the following content (update credentials as needed):
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/document_processing
EXTRACTION_API_URL=https://plankton-app-qajlk.ondigitalocean.app
MATCHING_API_URL=https://endeavor-interview-api-gzwki.ondigitalocean.app
```

### 6. Set up the database tables

```bash
python setup_db.py
```

## Running the Application

1. Make sure the virtual environment is activated.

2. Run the application:
```bash
python run.py
```

3. Access the web application at http://localhost:8000

4. Import the product catalog by clicking the "Import Catalog" button in the navigation bar.

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:
1. Make sure PostgreSQL is running.
2. Check your database credentials in the `.env` file.
3. Ensure the database exists (createdb document_processing).

### Import Catalog Issues

If catalog import fails:
1. Make sure the application is running.
2. Check if the `onsite_documents/unique_fastener_catalog.csv` file exists.

### Python Path Issues

If you encounter import errors:
1. Make sure you run the commands from the project's root directory.
2. Try installing the project in development mode: `pip install -e .` 
# Document Processing Application

A FastAPI application for automated document processing. This application allows users to upload PDF documents, extract line items, match them with products in a catalog, and export the results.

## Features

- PDF document upload and processing
- Extraction of line items from documents using an extraction API
- Matching line items to products using a matching API
- User verification and adjustment of matched products
- Product catalog search functionality
- Export results to CSV

## Technologies Used

- **Backend**: FastAPI, Python 3.8+
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **APIs**: External extraction and matching APIs

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Installation and Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd pdfprocess
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up PostgreSQL:
   - Install PostgreSQL if you haven't already
   - Create a new database:
     ```
     createdb document_processing
     ```
   - If you need to use different credentials, update them in the `.env` file

5. Configure environment variables in `.env` file:
   ```
   DATABASE_URL=postgresql://postgres:123456@localhost:5432/document_processing
   EXTRACTION_API_URL=https://plankton-app-qajlk.ondigitalocean.app
   MATCHING_API_URL=https://endeavor-interview-api-gzwki.ondigitalocean.app
   ```

6. Initialize database tables:
   ```
   python setup_db.py
   ```

## Running the Application

1. Start the application:
   ```
   python run.py
   ```
   Alternatively, you can use:
   ```
   python -m app.main
   ```

2. Access the web application at http://localhost:8000

3. Import the product catalog by clicking the "Import Catalog" button in the navigation bar when the application is running.

## Usage Instructions

1. First, import the product catalog by clicking the "Import Catalog" button in the navigation bar.

2. Upload a PDF document using the upload form on the home page.

3. Wait for the document to be processed. The system extracts line items and matches them to products in the catalog.

4. Review the matched products for each line item.

5. If needed, use the search feature to find and select a different product for any line item.

6. Export the results to a CSV file by clicking the "Export as CSV" button.

## API Documentation

API documentation is available at http://localhost:8000/docs when the application is running.

## Project Structure

```
pdfprocess/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_service.py
│   │   └── custom_matcher.py
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── images/
│   ├── templates/
│   │   ├── base.html
│   │   └── index.html
│   ├── __init__.py
│   └── main.py
├── onsite_documents/
│   ├── Example POs/
│   │   └── (PDF files)
│   └── unique_fastener_catalog.csv
├── tests/
│   ├── __init__.py
│   └── test_custom_matcher.py
├── .env
├── requirements.txt
├── setup_db.py
└── run.py
```

## Running Tests

Run the tests using pytest:
```
python -m pytest
```

## Demo Video

[Link to demo video]

## Future Improvements

1. Add user authentication
2. Improve matching algorithm with custom implementation
3. Add batch processing for multiple documents
4. Add document preview functionality
5. Implement more robust error handling 
# PDF Processing and Product Matching Application
video link: https://www.loom.com/share/76c3202df9864bcbb9c1898587a461a9
## Overview

This application is a comprehensive document processing system designed to extract content from PDF documents and match it with products in a catalog. It features a modern web interface, powerful OpenAI-powered PDF extraction, and intelligent product matching capabilities.

The system allows users to upload PDF documents, extract structured content, match each line item with potential products from a catalog, and export the processed data.

## Key Features

- **PDF Document Upload & Management**: Upload, view, and manage PDF documents through a user-friendly interface.
- **Advanced Text Extraction**: Extract structured text content from PDFs using OpenAI's API, automatically organizing the content in tabular format.
- **Intelligent Product Matching**: Automatically find the 3 most similar products in the catalog for each extracted line item using semantic similarity algorithms.
- **Interactive Table Editing**: Edit extracted table content with an intuitive interface.
- **Product Selection Interface**: Users can select the best matching product from the top 3 suggestions or search for alternatives.
- **Export Functionality**: Export processed data to Excel/CSV with product mappings.
- **Modern UI**: Responsive, Bootstrap-based interface with real-time feedback and notifications.

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **PDF Processing**: Direct integration with OpenAI API
- **Text Similarity**: Custom matching algorithms with SequenceMatcher

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Conda (recommended for environment management)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/pdfprocess.git
   cd pdfprocess
   ```

2. **Create and activate a Conda environment**:
   ```bash
   conda create -n python9 python=3.9
   conda activate python9
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the project root with the following variables:
   ```
   DATABASE_URL=postgresql://postgres:123456@localhost:5432/document_processing
   OPENAI_API_KEY=your_openai_api_key
   ```

5. **Initialize the database**:
   ```bash
   python setup_db.py
   ```

6. **Import product catalog (optional)**:
   Place your catalog CSV file at `onsite_documents/unique_fastener_catalog.csv`.

## Usage Guide

### Starting the Application

```bash
conda activate python9
python run.py
```

Access the web interface at `http://localhost:8000`.

### Working with Documents

1. **Upload a PDF**:
   - Click "Upload New Document" on the home page
   - Select a PDF file or drag and drop it into the upload area
   - Click "Upload Document"

2. **Process a Document**:
   - Navigate to the document view page
   - Click "Extract Content" to process the PDF
   - View the extracted content in the table format

3. **Match Products**:
   - For each table row, click the "Match" button to find similar products
   - Select the most appropriate match from the top 3 suggestions
   - Alternatively, use the custom search to find other product matches

4. **Edit Content**:
   - Click "Edit Table" to modify any extracted content
   - Make your changes and click "Save Changes"

5. **Export Results**:
   - Click "Export to Excel" to download the processed data
   - The export includes all table data and product mappings

## API Documentation

The application provides a RESTful API for programmatic access. Visit `http://localhost:8000/docs` for the interactive API documentation.

### Key Endpoints

- `POST /api/documents/upload`: Upload a new PDF document
- `POST /api/documents/{document_id}/extract`: Extract content from a document
- `POST /api/products/search`: Search for products in the catalog
- `POST /api/catalog/import`: Import a product catalog from CSV

## Implementation Details

### Custom PDF Extraction

The application uses OpenAI's API to directly process PDFs:

1. The PDF is uploaded directly to OpenAI
2. A structured extraction prompt is used to extract organized content
3. The response is formatted into a table structure for display
4. No preprocessing is required, handling a wide variety of PDF formats

### Custom Product Matching

Instead of using external services, the application implements a custom similarity algorithm to match extracted text with catalog products:

1. **Text Preprocessing**: Normalizes text for better comparison (lowercase, special character removal, etc.)
2. **Similarity Calculation**: Uses a sequence matching algorithm to determine text similarity
3. **Top-N Selection**: Returns the most relevant matches (default: 3)

## Troubleshooting

- **Database Connection Issues**: Ensure PostgreSQL is running and the connection string in `.env` is correct
- **PDF Processing Errors**: Check your OpenAI API key and verify the PDF is not corrupted
- **Product Catalog Not Found**: Make sure the CSV file exists in the specified location
- **Import Error**: Verify that the `extract_document_content_with_llm` function is properly imported

## Project Structure

```
pdfprocess/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
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
│   │   ├── pdf_extraction_service.py  # Custom OpenAI PDF extraction
│   │   └── custom_matcher.py          # Custom product matching implementation
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── document_view.html
│   ├── __init__.py
│   └── main.py
├── onsite_documents/
│   └── unique_fastener_catalog.csv
├── tests/
├── .env
├── requirements.txt
├── setup_db.py
└── run.py
```

## Development Guidelines

### Adding New Features

1. **Backend Changes**:
   - Add new routes in `app/api/routes.py`
   - Create/update models in `app/models/models.py`
   - Add service functions in the appropriate service files

2. **Frontend Changes**:
   - Modify templates in `app/templates/`
   - Add JavaScript functionality where needed
   - Ensure responsive design is maintained

### Running Tests

```bash
python -m pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- OpenAI for the powerful API used for PDF processing
- FastAPI team for the excellent web framework
- Bootstrap team for the frontend framework

---

For questions or issues, please open an issue on the repository or contact the maintainers. 
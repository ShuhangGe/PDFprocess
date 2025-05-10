import os
import csv
import json
import traceback
import shutil  # For file operations
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
import tempfile
import logging
from fastapi.responses import FileResponse
import xlsxwriter
import time

from app.db.database import get_db
from app.models.models import Document, LineItem, ProductCatalog, ProductMatch
from app.schemas.schemas import (
    Document as DocumentSchema,
    DocumentUploadResponse,
    UpdateMatchRequest,
    SearchProductRequest,
    ProductCatalog as ProductCatalogSchema
)
from app.services.document_service import extract_document_content as extract_content_service, match_line_items
from app.services.custom_matcher import match_line_items_custom, calculate_similarity, preprocess_text
from app.services.pdf_extraction_service import extract_document_content_with_llm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create directory for storing uploaded documents if it doesn't exist
UPLOAD_DIR = os.path.join("app", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF document and save it to disk.
    Returns document ID without processing content.
    """
    # Log the received file information
    logger.info(f"Uploading file: {file.filename}")
    
    # Check if file is PDF
    if not file.filename.endswith(".pdf"):
        logger.warning(f"Invalid file type: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted"
        )
    
    try:
        # Save document information to database (without processing)
        logger.info("Creating document record in database")
        db_document = Document(filename=file.filename)
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Create filename for saved PDF
        file_path = os.path.join(UPLOAD_DIR, f"document_{db_document.id}.pdf")
        
        # Save the file to disk
        logger.info(f"Saving file to {file_path}")
        with open(file_path, "wb") as pdf_file:
            content = await file.read()
            pdf_file.write(content)
        
        # Return basic information about the document
        return {
            "document_id": db_document.id,
            "filename": db_document.filename,
            "items": []  # No items processed yet
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading document: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/documents/{document_id}/extract")
async def extract_document_content(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Extract content from a previously uploaded PDF document.
    Uses the extraction API to identify line items.
    """
    logger.info(f"Extracting content from document with ID: {document_id}")
    
    try:
        # Get document from database
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if db_document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        # Path to saved PDF
        file_path = os.path.join(UPLOAD_DIR, f"document_{document_id}.pdf")
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDF file for document {document_id} not found"
            )
        
        # Extract content from document
        logger.info(f"Opening file: {file_path}")
        with open(file_path, "rb") as file_content:
            # Extract content from document
            logger.info("Calling extraction API")
            extracted_content = extract_content_service(file_content)
            
            # Process extracted line items
            if not extracted_content:
                logger.error("Extraction API returned empty content")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to extract content from document"
                )
            
            # Check if we received an error response
            if len(extracted_content) == 1 and "error" in extracted_content[0]:
                logger.warning(f"Extraction API error: {extracted_content[0]['error']}")
                # Return the error as a response instead of raising exception
                # This allows the frontend to display the error message
                return {
                    "document_id": db_document.id,
                    "filename": db_document.filename,
                    "items": extracted_content,
                    "error": extracted_content[0]['error']
                }
            
            logger.info(f"Extracted {len(extracted_content)} items")
            
            # Process results and save to database
            extracted_items = []
            
            # Check if the first item is a table structure item
            table_data = None
            if extracted_content and extracted_content[0].get("description") == "TABLE_STRUCTURE" and "table_data" in extracted_content[0]:
                table_data = extracted_content[0]["table_data"]
            
            # If we have table data, add it to the response
            if table_data:
                extracted_items.append({
                    "description": "TABLE_STRUCTURE",
                    "quantity": 1,
                    "table_data": table_data
                })
            
            # Process each item
            for item in extracted_content:
                # Skip the table structure item when saving individual items
                if item.get("description") == "TABLE_STRUCTURE":
                    continue
                
                if "description" not in item:
                    logger.warning(f"Skipping item without description: {item}")
                    continue
                
                description = item["description"]
                quantity = item.get("quantity", 1)
                
                # Create line item in database
                logger.info(f"Creating line item: {description}")
                db_line_item = LineItem(
                    document_id=db_document.id,
                    description=description,
                    quantity=quantity
                )
                db.add(db_line_item)
                db.flush()  # Get ID without committing transaction
                
                # Add line item to response
                extracted_item = {
                    "id": db_line_item.id,
                    "description": description,
                    "quantity": quantity,
                    "matches": []  # No matches yet
                }
                extracted_items.append(extracted_item)
            
            # Commit all database changes
            logger.info("Committing all database changes")
            db.commit()
            
            logger.info(f"Document extraction completed successfully: {db_document.id}")
            
            return {
                "document_id": db_document.id,
                "filename": db_document.filename,
                "items": extracted_items
            }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error extracting document content: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/documents/{document_id}/match")
async def match_document_items(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Match line items of a document to product catalog.
    Uses the matching API to find corresponding products.
    """
    logger.info(f"Matching items for document with ID: {document_id}")
    
    try:
        # Get document from database
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if db_document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        # Get line items for this document
        line_items = db.query(LineItem).filter(LineItem.document_id == document_id).all()
        
        if not line_items:
            logger.warning(f"No line items found for document {document_id}")
            return {
                "document_id": db_document.id,
                "filename": db_document.filename,
                "items": []
            }
        
        # Get line item descriptions for matching
        line_item_descriptions = [item.description for item in line_items]
        
        # Match line items to product catalog
        logger.info(f"Matching {len(line_item_descriptions)} line items to product catalog")
        matching_results = match_line_items(line_item_descriptions)
        
        # Process matches
        processed_items = []
        
        for item in line_items:
            description = item.description
            
            # Get matching products for this line item
            matches = matching_results.get(description, [])
            logger.info(f"Found {len(matches)} matches for: {description}")
            
            # Add matches to database
            for match_data in matches:
                # Find or create product in catalog
                product_desc = match_data["match"]
                db_product = db.query(ProductCatalog).filter_by(description=product_desc).first()
                
                if not db_product:
                    # Create new product in catalog if not exists
                    logger.info(f"Creating new product in catalog: {product_desc}")
                    db_product = ProductCatalog(description=product_desc)
                    db.add(db_product)
                    db.flush()
                
                # Create product match
                db_match = ProductMatch(
                    line_item_id=item.id,
                    product_id=db_product.id,
                    score=match_data["score"],
                    is_selected=False  # Initially not selected
                )
                db.add(db_match)
            
            # Add line item to response
            processed_item = {
                "id": item.id,
                "description": description,
                "quantity": item.quantity,
                "matches": [
                    {
                        "product_id": db.query(ProductCatalog).filter_by(description=m["match"]).first().id if db.query(ProductCatalog).filter_by(description=m["match"]).first() else None,
                        "description": m["match"],
                        "score": m["score"]
                    }
                    for m in matches
                ]
            }
            processed_items.append(processed_item)
        
        # Commit all database changes
        logger.info("Committing all database changes")
        db.commit()
        
        logger.info(f"Document matching completed successfully: {db_document.id}")
        
        return {
            "document_id": db_document.id,
            "filename": db_document.filename,
            "items": processed_items
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error matching document items: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/documents/{document_id}/process")
async def process_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Process a previously uploaded PDF document.
    This is a convenience method that calls extract and match in sequence.
    """
    logger.info(f"Processing document with ID: {document_id}")
    
    try:
        # First extract content
        extract_result = await extract_document_content(document_id, db)
        
        # Then match items
        match_result = await match_document_items(document_id, db)
        
        return match_result
    
    except HTTPException as e:
        # Propagate the HTTPException
        raise e
    
    except Exception as e:
        logger.error(f"Error in process_document: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during processing: {str(e)}"
        )

@router.get("/documents/{document_id}", response_model=DocumentSchema)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Get document by ID with all its line items and matches
    """
    db_document = db.query(Document).filter(Document.id == document_id).first()
    
    if db_document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    return db_document

@router.post("/matches/update")
def update_match(request: UpdateMatchRequest, db: Session = Depends(get_db)):
    """
    Update the selected product match for a line item
    """
    # Get the line item
    line_item = db.query(LineItem).filter(LineItem.id == request.line_item_id).first()
    
    if line_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Line item with ID {request.line_item_id} not found"
        )
    
    # Update matches
    # First, unselect all matches for this line item
    for match in db.query(ProductMatch).filter(ProductMatch.line_item_id == request.line_item_id):
        match.is_selected = False
    
    # Then, select the specified match
    match = db.query(ProductMatch).filter(
        ProductMatch.line_item_id == request.line_item_id,
        ProductMatch.product_id == request.selected_product_id
    ).first()
    
    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match not found for line item {request.line_item_id} and product {request.selected_product_id}"
        )
    
    match.is_selected = True
    
    # Commit changes
    db.commit()
    
    return {"success": True}

@router.post("/products/search", response_model=List[ProductCatalogSchema])
def search_products(request: SearchProductRequest, db: Session = Depends(get_db)):
    """
    Search for products in the catalog based on a query string
    Returns the top N most similar products based on the limit parameter
    """
    search_term = f"%{request.query}%"
    limit = request.limit  # Get the limit for top matches
    
    # First, get products using a broader LIKE search
    products = db.query(ProductCatalog).filter(
        or_(
            ProductCatalog.description.ilike(search_term),
            ProductCatalog.type.ilike(search_term),
            ProductCatalog.material.ilike(search_term),
            ProductCatalog.size.ilike(search_term),
            ProductCatalog.length.ilike(search_term)
        )
    ).all()
    
    # If no results or limited results, get more products to calculate similarity
    if len(products) < limit * 2:
        # Get more products to ensure we have enough candidates
        additional_products = db.query(ProductCatalog).limit(50).all()
        # Add only products not already in the list
        product_ids = {p.id for p in products}
        for product in additional_products:
            if product.id not in product_ids:
                products.append(product)
                product_ids.add(product.id)
    
    # Calculate similarity scores
    products_with_scores = []
    preprocessed_query = preprocess_text(request.query)
    
    for product in products:
        # Calculate similarity between query and product description
        score = calculate_similarity(preprocessed_query, product.description)
        products_with_scores.append((product, score))
    
    # Sort by similarity score in descending order
    products_with_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return only the top N products
    top_products = [product for product, _ in products_with_scores[:limit]]
    
    return top_products

@router.post("/catalog/import")
def import_catalog(db: Session = Depends(get_db)):
    """
    Import product catalog from CSV file
    """
    csv_file_path = "onsite_documents/unique_fastener_catalog.csv"
    
    try:
        # Check if file exists
        if not os.path.exists(csv_file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CSV file not found at {csv_file_path}"
            )
        
        # Read CSV file and import products
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Count rows for reporting
            count = 0
            
            for row in reader:
                # Check if product already exists
                existing_product = db.query(ProductCatalog).filter_by(description=row.get('Description', '')).first()
                
                if not existing_product:
                    # Create new product
                    product = ProductCatalog(
                        type=row.get('Type', ''),
                        material=row.get('Material', ''),
                        size=row.get('Size', ''),
                        length=row.get('Length', ''),
                        coating=row.get('Coating', ''),
                        thread_type=row.get('Thread Type', ''),
                        description=row.get('Description', '')
                    )
                    db.add(product)
                    count += 1
            
            # Commit all additions
            db.commit()
            
            return {"success": True, "imported": count}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing catalog: {str(e)}"
        )

@router.post("/custom-match")
def custom_match_items(request: dict):
    """
    Match line item descriptions to products using custom matching algorithm
    
    This is a bonus feature that shows a custom implementation of matching
    rather than using the external API.
    """
    try:
        # Get queries from request
        queries = request.get("queries", [])
        
        if not queries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No queries provided"
            )
        
        # Use custom matching algorithm
        results = match_line_items_custom(queries)
        
        return {
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in custom matching: {str(e)}"
        )

@router.get("/documents", response_model=List[DocumentSchema])
def get_all_documents(db: Session = Depends(get_db)):
    """
    Get all uploaded documents with their line items and matches
    """
    db_documents = db.query(Document).order_by(Document.upload_date.desc()).all()
    return db_documents

@router.get("/debug/status")
def debug_status():
    """
    Debug endpoint to check the status of the APIs and database
    """
    from app.services.document_service import EXTRACTION_API_URL, MATCHING_API_URL
    import platform
    import psycopg2
    import os
    
    status = {
        "server": {
            "python_version": platform.python_version(),
            "system": platform.system(),
            "node": platform.node()
        },
        "apis": {
            "extraction_api": EXTRACTION_API_URL,
            "matching_api": MATCHING_API_URL
        },
        "database": {
            "url": os.environ.get("DATABASE_URL", "Not set").split("@")[-1],  # Hide credentials
            "connection": "Not tested",
            "version": "Not available"
        }
    }
    
    # Test database connection
    try:
        conn_parts = os.environ.get("DATABASE_URL", "").split("/")
        db_name = conn_parts[-1]
        connection_string = "/".join(conn_parts[:-1])
        
        conn = psycopg2.connect(os.environ.get("DATABASE_URL", ""))
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        conn.close()
        
        status["database"]["connection"] = "OK"
        status["database"]["version"] = db_version[0] if db_version else "Unknown"
    except Exception as e:
        status["database"]["connection"] = "ERROR"
        status["database"]["error"] = str(e)
    
    # Test API connections
    import requests
    try:
        extraction_response = requests.get(f"{EXTRACTION_API_URL}/docs", timeout=5)
        status["apis"]["extraction_status"] = "OK" if extraction_response.ok else "ERROR"
        status["apis"]["extraction_code"] = extraction_response.status_code
    except Exception as e:
        status["apis"]["extraction_status"] = "ERROR"
        status["apis"]["extraction_error"] = str(e)
    
    try:
        matching_response = requests.get(f"{MATCHING_API_URL}/docs", timeout=5)
        status["apis"]["matching_status"] = "OK" if matching_response.ok else "ERROR"
        status["apis"]["matching_code"] = matching_response.status_code
    except Exception as e:
        status["apis"]["matching_status"] = "ERROR"
        status["apis"]["matching_error"] = str(e)
    
    return status 

@router.delete("/documents/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """
    Delete a document and all its associated data (line items, matches, and PDF file)
    """
    logger.info(f"Deleting document with ID: {document_id}")
    
    try:
        # Get document from database
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if db_document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        # Prepare the path to the PDF file
        file_path = os.path.join(UPLOAD_DIR, f"document_{document_id}.pdf")
        
        # Delete document from database (cascades to line items and matches due to relationship settings)
        db.delete(db_document)
        db.commit()
        
        # Delete the PDF file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
        
        return {"success": True, "message": f"Document {document_id} deleted successfully"}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting document: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/documents/{document_id}/pdf")
async def get_document_pdf(document_id: int):
    """
    Serve the original PDF file for a given document
    """
    file_path = os.path.join(UPLOAD_DIR, f"document_{document_id}.pdf")
    
    if not os.path.exists(file_path):
        logger.error(f"PDF file not found: {file_path}")
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    return FileResponse(file_path, media_type="application/pdf")

@router.post("/documents/{document_id}/export-excel")
async def export_document_to_excel(
    document_id: int,
    table_data: dict,
    db: Session = Depends(get_db)
):
    """
    Generate an Excel file from the table data and document mappings
    """
    logger.info(f"Exporting document {document_id} to Excel")
    
    try:
        # Verify document exists
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.warning(f"Document not found: {document_id}")
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Create a temporary file for the Excel document
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        # Create a workbook and add worksheets
        workbook = xlsxwriter.Workbook(temp_file_path)
        
        # Create formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#0d6efd',
            'color': 'white',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'border': 1
        })
        
        # Add Data worksheet
        data_sheet = workbook.add_worksheet("Document Data")
        
        # Write headers
        columns = table_data.get("columns", ["Content"])
        for col_idx, header in enumerate(columns):
            data_sheet.write(0, col_idx, header, header_format)
        
        # Write data rows
        rows = table_data.get("rows", [])
        for row_idx, row in enumerate(rows):
            if isinstance(row, list):
                # Array-style row
                for col_idx, cell in enumerate(row):
                    data_sheet.write(row_idx + 1, col_idx, cell, cell_format)
            elif isinstance(row, dict):
                # Object-style row with key/value pairs
                for col_idx, col_name in enumerate(columns):
                    data_sheet.write(row_idx + 1, col_idx, row.get(col_name, ""), cell_format)
        
        # Add Mappings worksheet if mappings are provided
        if "mappings" in table_data and len(table_data["mappings"]) > 0:
            mappings_sheet = workbook.add_worksheet("Product Mappings")
            
            # Write headers for mappings
            mapping_headers = ["Row", "Original Content", "Mapped Product ID", "Mapped Product Description"]
            for col_idx, header in enumerate(mapping_headers):
                mappings_sheet.write(0, col_idx, header, header_format)
            
            # Write mapping data
            for map_idx, mapping in enumerate(table_data["mappings"]):
                mappings_sheet.write(map_idx + 1, 0, mapping.get("rowIndex", 0) + 1, cell_format)
                mappings_sheet.write(map_idx + 1, 1, mapping.get("originalContent", ""), cell_format)
                mappings_sheet.write(map_idx + 1, 2, mapping.get("productId", ""), cell_format)
                mappings_sheet.write(map_idx + 1, 3, mapping.get("productDescription", ""), cell_format)
            
            # Auto-fit columns in mappings sheet
            mappings_sheet.autofit()
        
        # Add document info sheet
        info_sheet = workbook.add_worksheet("Document Info")
        
        # Write document info
        info_sheet.write(0, 0, "Document ID:", workbook.add_format({'bold': True}))
        info_sheet.write(0, 1, document_id)
        info_sheet.write(1, 0, "Filename:", workbook.add_format({'bold': True}))
        info_sheet.write(1, 1, document.filename)
        info_sheet.write(2, 0, "Upload Date:", workbook.add_format({'bold': True}))
        info_sheet.write(2, 1, document.upload_date.strftime("%Y-%m-%d %H:%M:%S"))
        info_sheet.write(3, 0, "Export Date:", workbook.add_format({'bold': True}))
        info_sheet.write(3, 1, time.strftime("%Y-%m-%d %H:%M:%S"))
        
        # Auto-fit columns in data sheet
        data_sheet.autofit()
        
        # Close the workbook
        workbook.close()
        
        # Return the Excel file
        filename = f"document_{document_id}_export.xlsx"
        return FileResponse(
            path=temp_file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    except Exception as e:
        logger.error(f"Error exporting to Excel: {str(e)}")
        if 'temp_file_path' in locals():
            try:
                os.remove(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error exporting to Excel: {str(e)}") 
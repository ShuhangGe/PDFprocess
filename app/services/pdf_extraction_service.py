"""
PDF Extraction Service using OpenAI API.

This service extracts text content from PDF documents and formats it as a table.
"""

import os
import time
import logging
import tempfile
import json
from typing import List, Dict, Any, BinaryIO
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_line_items_with_openai_file_processing(file: BinaryIO) -> List[Dict[str, Any]]:
    """
    Extract text content from a PDF using OpenAI and format it as a table
    This uploads the PDF directly to OpenAI and returns the content in a table format
    """
    try:
        # Save the file temporarily so we can upload it with a reliable file path
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file_path = temp_file.name
            # Reset file pointer to beginning and write the contents
            file.seek(0)
            temp_file.write(file.read())
        
        logger.info(f"Temporary file created at {temp_file_path}")
        
        try:
            # Upload the file directly to OpenAI
            logger.info("Uploading PDF to OpenAI...")
            uploaded_file = client.files.create(
                file=open(temp_file_path, "rb"),
                purpose="user_data"  # Use user_data purpose for files
            )
            logger.info(f"File uploaded with ID: {uploaded_file.id}")
            
            # Create a prompt for extracting text as a table
            prompt = """
            Please extract all text content from this PDF document and format it as a table.
            
            Rules:
            1. Identify any tabular data in the document and preserve its structure
            2. If the document doesn't contain tabular data, format the text in a meaningful way with appropriate columns
            3. For general text, create columns like "Section" and "Content"
            4. For invoices or purchase orders, identify columns like "Item", "Description", "Quantity", "Price" etc.
            
            Format your response as a JSON object with the following structure:
            {
              "table_title": "Document Content",
              "columns": ["Column1", "Column2", "Column3"],
              "rows": [
                ["Row1-Col1", "Row1-Col2", "Row1-Col3"],
                ["Row2-Col1", "Row2-Col2", "Row2-Col3"]
              ]
            }
            
            The column names should reflect the type of content in the document.
            Include all the text content from the document, organized in a logical table structure.
            """
            
            # Process the PDF using the file ID
            logger.info(f"Processing PDF with OpenAI (file ID: {uploaded_file.id})...")
            response = client.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_file",
                                "file_id": uploaded_file.id,
                            },
                            {
                                "type": "input_text",
                                "text": prompt,
                            },
                        ]
                    }
                ]
            )
            
            # Extract content from the response
            content = ""
            try:
                # Based on the response structure:
                # Response.output[0].content[0].text is where the text content is
                if hasattr(response, 'output') and response.output:
                    # Access the first message in the output array
                    output_message = response.output[0]
                    if hasattr(output_message, 'content') and output_message.content:
                        # Access the first content item in the message
                        content_item = output_message.content[0]
                        if hasattr(content_item, 'text'):
                            # This is where the actual text is
                            content = content_item.text
                            logger.info("Successfully extracted text from response")
                        else:
                            content = str(content_item)
                    else:
                        content = str(output_message)
                else:
                    content = str(response)
            except Exception as e:
                logger.error(f"Error extracting content from response: {e}")
                content = str(response)
            
            logger.info(f"OpenAI response received: {len(content)} characters")
            
            # Try to parse the JSON table structure
            try:
                # Look for JSON object in the text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                
                if json_match:
                    json_text = json_match.group(0)
                    table_data = json.loads(json_text)
                    
                    # Create a standardized table structure
                    table = {
                        "title": table_data.get("table_title", "Document Content"),
                        "columns": table_data.get("columns", ["Content"]),
                        "rows": table_data.get("rows", [])
                    }
                    
                    # If the JSON doesn't have the expected structure, try to extract what we can
                    if "rows" not in table_data and "data" in table_data:
                        table["rows"] = table_data["data"]
                    
                    # Create line items from the table data
                    items = []
                    
                    # Create a special first item that contains the table structure
                    items.append({
                        "description": "TABLE_STRUCTURE",
                        "quantity": 1,
                        "table_data": table
                    })
                    
                    # Add individual rows as line items for backwards compatibility
                    for row in table["rows"]:
                        if isinstance(row, list) and len(row) > 0:
                            # Join all columns with a delimiter for display
                            row_text = " | ".join([str(cell) for cell in row])
                            items.append({
                                "description": row_text,
                                "quantity": 1
                            })
                    
                    logger.info(f"Successfully parsed table with {len(table['rows'])} rows and {len(table['columns'])} columns")
                    
                else:
                    # If no JSON found, create a basic table from the text
                    logger.warning("No JSON table found in response, creating basic table")
                    lines = content.strip().split('\n')
                    
                    # Create a basic single-column table
                    table = {
                        "title": "Document Content",
                        "columns": ["Content"],
                        "rows": [[line] for line in lines if line.strip()]
                    }
                    
                    items = []
                    
                    # Create a special first item that contains the table structure
                    items.append({
                        "description": "TABLE_STRUCTURE",
                        "quantity": 1,
                        "table_data": table
                    })
                    
                    # Add individual lines as items for backwards compatibility
                    for line in lines:
                        if line.strip():
                            items.append({
                                "description": line.strip(),
                                "quantity": 1
                            })
            
            except Exception as e:
                logger.error(f"Error parsing table data: {e}")
                # Fall back to simple line-by-line output
                lines = content.strip().split('\n')
                
                # Create a basic single-column table
                table = {
                    "title": "Document Content",
                    "columns": ["Content"],
                    "rows": [[line] for line in lines if line.strip()]
                }
                
                items = []
                
                # Create a special first item that contains the table structure
                items.append({
                    "description": "TABLE_STRUCTURE",
                    "quantity": 1,
                    "table_data": table
                })
                
                # Add individual lines as items for backwards compatibility
                for line in lines:
                    if line.strip():
                        items.append({
                            "description": line.strip(),
                            "quantity": 1
                        })
            
            logger.info(f"Extracted table with {len(items)-1} data rows")
            
            # Clean up the uploaded file on OpenAI's servers
            try:
                client.files.delete(uploaded_file.id)
                logger.info(f"Deleted file {uploaded_file.id} from OpenAI")
            except Exception as e:
                logger.warning(f"Failed to delete file from OpenAI: {str(e)}")
            
            return items
            
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
                logger.info(f"Temporary file {temp_file_path} removed")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {e}")
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF with OpenAI: {str(e)}")
        return [{"description": f"Error extracting text with OpenAI: {str(e)}", "quantity": 1}]


def extract_document_content_with_llm(file: BinaryIO) -> List[Dict[str, Any]]:
    """
    Main function to extract content from PDF document using OpenAI
    """
    try:
        # Log file size
        file_content = file.read()
        file_size = len(file_content)
        logger.info(f"PDF file size: {file_size} bytes")
        
        # Reset file pointer for reading
        file.seek(0)
        
        # Extract line items using OpenAI's file processing
        logger.info("Extracting line items using OpenAI file processing")
        start_time = time.time()
        line_items = extract_line_items_with_openai_file_processing(file)
        logger.info(f"OpenAI extraction completed in {time.time() - start_time:.2f} seconds")
        
        # If no line items were found
        if not line_items:
            logger.warning("No line items found in document")
            return [{
                "description": "No line items found in document",
                "quantity": 1,
                "error": "The document doesn't appear to contain any recognizable line items"
            }]
        
        logger.info(f"Successfully extracted {len(line_items)} line items")
        return line_items
    
    except Exception as e:
        logger.error(f"Error in document extraction process: {str(e)}")
        return [{
            "description": f"Error processing document: {str(e)}",
            "quantity": 1,
            "error": str(e)
        }] 
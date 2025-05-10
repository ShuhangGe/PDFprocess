import os
import json
import requests
from typing import List, Dict, Any, BinaryIO
from dotenv import load_dotenv

# Import our new OpenAI PDF extraction service
from app.services.pdf_extraction_service import extract_document_content_with_llm
# Import the custom matcher
from app.services.custom_matcher import match_line_items_custom

# Load environment variables
load_dotenv()

EXTRACTION_API_URL = os.getenv("EXTRACTION_API_URL")
MATCHING_API_URL = os.getenv("MATCHING_API_URL")


def extract_document_content(file: BinaryIO) -> List[Dict[str, Any]]:
    """
    Extract content from PDF document using OpenAI instead of external API
    """
    try:
        # Use our OpenAI-based extraction service
        return extract_document_content_with_llm(file)
    except Exception as e:
        print(f"Error extracting document content with OpenAI: {str(e)}")
        return [{
            "description": f"Error extracting content: {str(e)}",
            "quantity": 1,
            "error": str(e)
        }]


def match_line_items(descriptions: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Match line item descriptions to products in catalog using custom matching
    """
    try:
        # Use our custom matching implementation instead of external API
        matching_results = match_line_items_custom(descriptions)
        return matching_results
    except Exception as e:
        print(f"Error in matching: {str(e)}")
        return {} 
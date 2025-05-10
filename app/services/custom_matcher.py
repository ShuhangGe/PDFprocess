"""
Custom matching implementation for document line items to product catalog.

This is a simple implementation that could replace the external API for matching.
"""

import csv
import re
from typing import List, Dict, Any
import os
from difflib import SequenceMatcher

def load_product_catalog(csv_file_path: str) -> List[Dict[str, str]]:
    """
    Load product catalog from CSV file
    """
    catalog = []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                catalog.append(row)
    except Exception as e:
        print(f"Error loading catalog: {e}")
        return []
    
    return catalog

def preprocess_text(text: str) -> str:
    """
    Preprocess text for better matching
    - Convert to lowercase
    - Remove special characters
    - Remove extra spaces
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity score between two text strings
    Returns a score between 0-100
    """
    # Preprocess texts
    text1 = preprocess_text(text1)
    text2 = preprocess_text(text2)
    
    # Use SequenceMatcher to calculate similarity
    matcher = SequenceMatcher(None, text1, text2)
    similarity = matcher.ratio() * 100
    
    return similarity

def match_line_items_custom(descriptions: List[str], top_n: int = 5) -> Dict[str, List[Dict[str, Any]]]:
    """
    Match line item descriptions to products in catalog
    Returns top N matches for each description
    """
    # Path to product catalog
    csv_file_path = "onsite_documents/unique_fastener_catalog.csv"
    
    # Check if file exists
    if not os.path.exists(csv_file_path):
        print(f"CSV file not found at {csv_file_path}")
        return {}
    
    # Load product catalog
    catalog = load_product_catalog(csv_file_path)
    
    # Dictionary to store results
    results = {}
    
    # Process each description
    for description in descriptions:
        # Skip empty descriptions
        if not description:
            continue
        
        # Calculate similarity scores for all products
        matches = []
        
        for product in catalog:
            product_desc = product.get('Description', '')
            score = calculate_similarity(description, product_desc)
            
            matches.append({
                "match": product_desc,
                "score": score
            })
        
        # Sort by score in descending order
        matches.sort(key=lambda x: x["score"], reverse=True)
        
        # Take top N matches
        results[description] = matches[:top_n]
    
    return results 
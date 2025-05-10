import os
import sys
import pytest
from unittest.mock import patch, mock_open

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.custom_matcher import (
    preprocess_text, 
    calculate_similarity,
    load_product_catalog,
    match_line_items_custom
)

def test_preprocess_text():
    """Test text preprocessing function"""
    # Test lowercase conversion
    assert preprocess_text("TEST") == "test"
    
    # Test special character removal
    assert preprocess_text("test!@#$%^&*()") == "test"
    
    # Test extra space removal
    assert preprocess_text("  test  with  spaces  ") == "test with spaces"
    
    # Test combined preprocessing
    assert preprocess_text("  TEST!@#$%^&*()  with  SPACES  ") == "test with spaces"

def test_calculate_similarity():
    """Test similarity calculation function"""
    # Test identical strings
    assert calculate_similarity("test", "test") == 100.0
    
    # Test completely different strings
    assert calculate_similarity("test", "xxxx") < 50.0
    
    # Test similar strings
    assert calculate_similarity("test string", "test strings") > 90.0
    
    # Test case insensitivity
    assert calculate_similarity("TEST", "test") == 100.0

def test_load_product_catalog():
    """Test loading product catalog from CSV"""
    # Mock CSV content
    mock_csv_content = "Type,Material,Size,Length,Coating,Thread Type,Description\n" \
                      "Bolt,Steel,M4,10mm,Zinc Plated,Coarse,Steel Bolt M4 10mm Zinc Plated Coarse\n" \
                      "Bolt,Steel,M4,10mm,Zinc Plated,Fine,Steel Bolt M4 10mm Zinc Plated Fine"
    
    # Patch open function to return mock CSV content
    with patch("builtins.open", mock_open(read_data=mock_csv_content)):
        catalog = load_product_catalog("mock_path.csv")
        
        # Check if catalog is loaded correctly
        assert len(catalog) == 2
        assert catalog[0]["Description"] == "Steel Bolt M4 10mm Zinc Plated Coarse"
        assert catalog[1]["Type"] == "Bolt"

@patch("os.path.exists", return_value=True)
@patch("app.services.custom_matcher.load_product_catalog")
def test_match_line_items_custom(mock_load_catalog, mock_exists):
    """Test custom matching function"""
    # Mock catalog
    mock_catalog = [
        {"Description": "Steel Bolt M4 10mm Zinc Plated Coarse"},
        {"Description": "Steel Bolt M4 10mm Zinc Plated Fine"},
        {"Description": "Aluminum Screw M5 20mm Uncoated Fine"}
    ]
    mock_load_catalog.return_value = mock_catalog
    
    # Test matching
    descriptions = ["Steel Bolt M4", "Aluminum Screw"]
    results = match_line_items_custom(descriptions, top_n=2)
    
    # Check if results are returned correctly
    assert len(results) == 2
    assert len(results["Steel Bolt M4"]) == 2  # Only top 2 should be returned
    
    # Check if first match for "Steel Bolt M4" has higher score than second match
    assert results["Steel Bolt M4"][0]["score"] > results["Steel Bolt M4"][1]["score"]
    
    # Check if match contains correct fields
    assert "match" in results["Steel Bolt M4"][0]
    assert "score" in results["Steel Bolt M4"][0] 
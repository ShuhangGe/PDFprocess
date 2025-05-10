import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv()
EXTRACTION_API_URL = os.getenv("EXTRACTION_API_URL")

def test_with_curl_approach():
    """
    Test the extraction API using an approach that mimics the successful curl command
    """
    # Set the correct endpoint URL
    extraction_endpoint = f"{EXTRACTION_API_URL}/extraction_api"
    print(f"Testing endpoint: {extraction_endpoint}")
    
    # Try with the invoice PDF we created
    pdf_path = "invoice.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found")
        return
    
    with open(pdf_path, 'rb') as f:
        file_content = f.read()
    
    print(f"File size: {len(file_content)} bytes")
    
    try:
        # Setup the files parameter exactly as it would be in curl -F "file=@filename.pdf"
        files = {'file': ('invoice.pdf', file_content, 'application/pdf')}
        
        # Set headers
        headers = {'accept': 'application/json'}
        
        # Make the request with verbose output
        print("Making request with files parameter:")
        print(f"  - File name: invoice.pdf")
        print(f"  - Content-Type: application/pdf")
        print(f"  - File size: {len(file_content)} bytes")
        
        response = requests.post(
            extraction_endpoint,
            files=files,
            headers=headers,
            timeout=30
        )
        
        print(f"\nResponse status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response body: {response.text[:1000]}")
        
        if response.status_code == 200:
            print("\nRequest succeeded!")
            try:
                result = response.json()
                print(f"Extracted {len(result)} items")
                for idx, item in enumerate(result[:5], 1):  # Show first 5 items
                    print(f"Item {idx}: {item}")
                if len(result) > 5:
                    print(f"... and {len(result) - 5} more items")
            except json.JSONDecodeError:
                print("Warning: Response is not valid JSON")
        else:
            print("\nRequest failed!")
            
            # Try to parse the error response
            try:
                error = response.json()
                print(f"Error details: {error}")
            except json.JSONDecodeError:
                print(f"Raw error response: {response.text}")
    
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    test_with_curl_approach() 
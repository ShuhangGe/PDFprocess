#!/usr/bin/env python3
"""
Test script for the extraction API
"""

import os
import sys
import requests
import json
import urllib3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EXTRACTION_API_URL = os.getenv("EXTRACTION_API_URL")

def test_extraction_api():
    # Set the correct endpoint URL
    extraction_endpoint = f"{EXTRACTION_API_URL}/extraction_api"
    print(f"Testing endpoint: {extraction_endpoint}")
    
    # Try with a sample PDF downloaded from the web
    pdf_path = "sample.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found")
        return
    
    with open(pdf_path, 'rb') as f:
        file_content = f.read()
    
    print(f"File size: {len(file_content)} bytes")
    
    # Method 1: Standard requests with files parameter
    print("\n=== Testing Method 1 ===")
    try:
        files = {'file': ('sample.pdf', file_content, 'application/pdf')}
        headers = {'accept': 'application/json'}
        
        response = requests.post(
            extraction_endpoint,
            headers=headers,
            files=files,
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Method 1 succeeded!")
            return  # If successful, no need to try other methods
        else:
            print("Method 1 failed")
    except Exception as e:
        print(f"Error in Method 1: {str(e)}")
    
    # Method 2: Raw binary data
    print("\n=== Testing Method 2 ===")
    try:
        files = {'file': file_content}
        headers = {'accept': 'application/json'}
        
        response = requests.post(
            extraction_endpoint,
            headers=headers,
            files=files,
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Method 2 succeeded!")
            return
        else:
            print("Method 2 failed")
    except Exception as e:
        print(f"Error in Method 2: {str(e)}")
    
    # Method 3: Using urllib3 to encode multipart form data
    print("\n=== Testing Method 3 ===")
    try:
        fields = {
            'file': ('sample.pdf', file_content, 'application/pdf')
        }
        
        body, content_type = urllib3.filepost.encode_multipart_formdata(fields)
        
        headers = {
            'accept': 'application/json',
            'Content-Type': content_type
        }
        
        response = requests.post(
            extraction_endpoint,
            headers=headers,
            data=body,
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Method 3 succeeded!")
            return
        else:
            print("Method 3 failed")
    except Exception as e:
        print(f"Error in Method 3: {str(e)}")
    
    # Method 4: Using requests-toolbelt MultipartEncoder
    print("\n=== Testing Method 4 ===")
    try:
        from requests_toolbelt import MultipartEncoder
        
        m = MultipartEncoder(
            fields={'file': ('sample.pdf', file_content, 'application/pdf')}
        )
        
        headers = {
            'accept': 'application/json',
            'Content-Type': m.content_type
        }
        
        response = requests.post(
            extraction_endpoint,
            headers=headers,
            data=m,
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Method 4 succeeded!")
            return
        else:
            print("Method 4 failed")
    except Exception as e:
        print(f"Error in Method 4: {str(e)}")
    
    # Method 5: Using data parameter with JSON payload
    print("\n=== Testing Method 5 ===")
    try:
        import base64
        
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        payload = {
            "file": encoded_content
        }
        
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            extraction_endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Method 5 succeeded!")
            return
        else:
            print("Method 5 failed")
    except Exception as e:
        print(f"Error in Method 5: {str(e)}")
    
    print("\nTest completed")

if __name__ == "__main__":
    test_extraction_api() 
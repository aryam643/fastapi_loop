"""
Simple test script to verify API functionality
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_api():
    """Test the API endpoints"""
    print("Testing Store Monitoring API...")
    
    # Test root endpoint
    print("\n1. Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test health check
    print("\n2. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test trigger report
    print("\n3. Testing trigger report...")
    response = requests.post(f"{BASE_URL}/trigger_report")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        report_data = response.json()
        report_id = report_data["report_id"]
        print(f"Report ID: {report_id}")
        
        # Test get report status (should be running initially)
        print("\n4. Testing get report status (running)...")
        response = requests.get(f"{BASE_URL}/get_report/{report_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Wait a bit and check again
        print("\n5. Waiting 10 seconds and checking again...")
        time.sleep(10)
        response = requests.get(f"{BASE_URL}/get_report/{report_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            if response.headers.get('content-type') == 'text/csv':
                print("Report completed! CSV file received.")
                print(f"Content length: {len(response.content)} bytes")
            else:
                print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    else:
        print(f"Error triggering report: {response.text}")
    
    # Test invalid report ID
    print("\n6. Testing invalid report ID...")
    response = requests.get(f"{BASE_URL}/get_report/invalid-id")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_api()

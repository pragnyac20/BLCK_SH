#!/usr/bin/env python3
"""
Example usage of the Blockchain Education Data Management System API
This script demonstrates how to interact with the system
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    print(f"{'='*60}\n")

def main():
    """Main execution flow"""
    
    print("\n" + "="*60)
    print("Blockchain Education System - Example Usage")
    print("="*60)
    
    # 1. Health Check
    print("\n1. Checking system health...")
    response = requests.get(f"{BASE_URL}/api/health")
    print_response("Health Check", response)
    
    # 2. Create a student
    print("\n2. Creating a student...")
    student_data = {
        "student_id": "S2024001",
        "name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "public_metadata": {
            "program": "Computer Science",
            "year": 2024,
            "enrollment_date": "2024-08-15"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/students", json=student_data)
    print_response("Create Student", response)
    
    # 3. Get student details
    print("\n3. Retrieving student details...")
    response = requests.get(f"{BASE_URL}/api/students/S2024001")
    print_response("Get Student", response)
    
    # 4. Issue a single academic record
    print("\n4. Issuing an academic record...")
    record_data = {
        "student_id": "S2024001",
        "payload": {
            "course_code": "CS301",
            "course_name": "Data Structures and Algorithms",
            "grade": "A",
            "credits": 4,
            "semester": "Fall 2024",
            "instructor": "Dr. Smith",
            "date_issued": "2024-12-15"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/issue", json=record_data)
    print_response("Issue Record", response)
    
    if response.status_code == 201:
        record_id = response.json()['record_id']
        
        # 5. Get record details (encrypted)
        print("\n5. Retrieving encrypted record...")
        response = requests.get(f"{BASE_URL}/api/records/{record_id}")
        print_response("Get Record (Encrypted)", response)
        
        # 6. Decrypt record (authorized access)
        print("\n6. Decrypting record (authorized access)...")
        response = requests.get(f"{BASE_URL}/api/records/{record_id}/decrypt")
        print_response("Decrypt Record", response)
        
        # 7. Verify record integrity
        print("\n7. Verifying record integrity...")
        time.sleep(1)  # Give blockchain time to commit
        response = requests.get(f"{BASE_URL}/api/verify/{record_id}")
        print_response("Verify Record", response)
    
    # 8. Create another student for batch demo
    print("\n8. Creating another student for batch processing...")
    student_data2 = {
        "student_id": "S2024002",
        "name": "Bob Williams",
        "email": "bob.williams@example.com",
        "public_metadata": {
            "program": "Information Science",
            "year": 2024
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/students", json=student_data2)
    print_response("Create Second Student", response)
    
    # 9. Batch issue multiple records
    print("\n9. Batch issuing multiple records...")
    batch_data = {
        "records": [
            {
                "student_id": "S2024001",
                "payload": {
                    "course_code": "CS302",
                    "course_name": "Database Management Systems",
                    "grade": "A+",
                    "credits": 4,
                    "semester": "Fall 2024"
                }
            },
            {
                "student_id": "S2024001",
                "payload": {
                    "course_code": "CS303",
                    "course_name": "Operating Systems",
                    "grade": "A",
                    "credits": 3,
                    "semester": "Fall 2024"
                }
            },
            {
                "student_id": "S2024002",
                "payload": {
                    "course_code": "IS201",
                    "course_name": "Information Security",
                    "grade": "B+",
                    "credits": 3,
                    "semester": "Fall 2024"
                }
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/batch-issue", json=batch_data)
    print_response("Batch Issue Records", response)
    
    # 10. Get all transactions
    print("\n10. Retrieving all transactions...")
    response = requests.get(f"{BASE_URL}/api/transactions")
    print_response("Get All Transactions", response)
    
    print("\n" + "="*60)
    print("Example usage completed successfully!")
    print("="*60 + "\n")
    
    # Summary
    print("\nSummary of Operations:")
    print("✓ System health checked")
    print("✓ 2 students created")
    print("✓ 1 individual record issued")
    print("✓ Record encrypted, decrypted, and verified")
    print("✓ 3 records issued in batch with Merkle tree")
    print("✓ Transaction history retrieved")
    print("\nAll operations completed successfully!")
    print("\nYou can now:")
    print("- View the SQLite database: education_records.db")
    print("- Check transaction logs")
    print("- Verify any record using its record_id")
    print("- Issue more records or create more students")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to the API server")
        print("Please ensure the Flask application is running:")
        print("  python app/app.py")
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
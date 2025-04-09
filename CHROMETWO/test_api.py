"""
Simple test script to verify API connectivity
"""
import requests
import time
import sys

def test_api_connection():
    print("Testing API connection...")
    try:
        response = requests.get('http://localhost:5000/api/debug', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is running!")
            print(f"Database exists: {data.get('database_exists', 'Unknown')}")
            print(f"Items in database: {data.get('item_count', 'Unknown')}")
            return True
        else:
            print(f"❌ API returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the Flask server is running on port 5000.")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    if not test_api_connection():
        print("\nTroubleshooting tips:")
        print("1. Make sure you've started the Flask server with 'python app.py'")
        print("2. Check if port 5000 is already in use by another application")
        print("3. Verify there are no firewall or network issues blocking connections")
        sys.exit(1)
    
    print("\nAPI is accessible. You can now use the web interface.")

if __name__ == "__main__":
    main()

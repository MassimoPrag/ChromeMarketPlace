"""
Debugging script to help troubleshoot API issues
"""
import requests
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

API_URL = 'http://localhost:5000/api'

def check_env_keys():
    """Check environment variables"""
    print("Checking environment variables...")
    google_key = os.getenv('GOOGLE_API_KEY')
    if not google_key:
        print("❌ GOOGLE_API_KEY is missing in environment")
    else:
        print(f"✅ GOOGLE_API_KEY is set (starts with: {google_key[:5]}...)")
    
    return google_key is not None

def test_api_routes():
    """Test all API routes"""
    routes = {
        'debug': 'GET',
        'items': 'GET', 
        'test_scrape': 'GET'
    }
    
    results = {}
    
    print("\nTesting API routes...")
    for route, method in routes.items():
        try:
            url = f"{API_URL}/{route}"
            print(f"Testing {method} {url}...")
            
            if method == 'GET':
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {route} - Status code: {response.status_code}")
                results[route] = True
            else:
                print(f"❌ {route} - Status code: {response.status_code}")
                results[route] = False
                
            # Print response data for debugging
            try:
                print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
            except:
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ {route} - Error: {str(e)}")
            results[route] = False
    
    return results

def main():
    print("=" * 50)
    print("Chrome Hearts API Diagnostics")
    print("=" * 50)
    
    env_good = check_env_keys()
    if not env_good:
        print("\n⚠️ Environment variables issues detected")
    
    # Try to connect to API
    try:
        results = test_api_routes()
        success = all(results.values())
        
        if success:
            print("\n✅ All API routes are working!")
        else:
            print("\n⚠️ Some API routes failed!")
            
        # Test scrape specifically if debug endpoint works
        if results.get('debug', False) and not results.get('test_scrape', True):
            print("\nTrying scrape test...")
            try:
                response = requests.get(f"{API_URL}/test_scrape", timeout=60)
                if response.status_code == 200:
                    print("✅ Scraping test successful!")
                else:
                    print(f"❌ Scraping test failed with status {response.status_code}")
                    print(f"Response: {response.text[:500]}")
            except Exception as e:
                print(f"❌ Scraping test error: {str(e)}")
                
    except Exception as e:
        print(f"\n❌ Cannot connect to API: {str(e)}")
        print("\nMake sure the Flask server is running with 'python app.py'")
    
    print("\nDiagnostic complete.")

if __name__ == "__main__":
    main()

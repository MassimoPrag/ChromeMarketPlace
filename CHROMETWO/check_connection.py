"""
Connection checker script for Chrome Hearts Database application
This script helps diagnose common issues with localhost connections
"""
import socket
import requests
import sys
import os
import subprocess
import platform

def check_port(port):
    """Check if a port is open on localhost"""
    print(f"Checking if port {port} is open...")
    
    # Check if port is in use
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    if result == 0:
        print(f"✅ Port {port} is OPEN (something is listening)")
    else:
        print(f"❌ Port {port} is CLOSED (nothing is listening)")
    sock.close()
    
    return result == 0

def check_server_running():
    """Check if Flask server is running"""
    print("\nChecking if Flask server is running...")
    
    # Check for running processes
    if platform.system() == "Windows":
        cmd = "tasklist | findstr python"
    else:  # macOS or Linux
        cmd = "ps aux | grep python | grep -v grep"
    
    try:
        output = subprocess.check_output(cmd, shell=True).decode('utf-8')
        if "python" in output:
            print("✅ Python processes found running:")
            for line in output.splitlines():
                print(f"  {line}")
        else:
            print("❌ No Python processes found running")
    except subprocess.CalledProcessError:
        print("❌ No Python processes found running")

def test_connection(url):
    """Test a connection to a URL"""
    print(f"\nTesting connection to {url}...")
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Connection successful (status code: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed: Could not connect to server")
    except requests.exceptions.Timeout:
        print("❌ Connection failed: Request timed out")
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
    return False

def check_localhost_config():
    """Check localhost configuration"""
    print("\nChecking localhost configuration...")
    
    # Check hosts file
    if platform.system() == "Windows":
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    else:  # macOS or Linux
        hosts_path = "/etc/hosts"
    
    try:
        with open(hosts_path, 'r') as f:
            hosts_content = f.read()
        
        if "localhost" in hosts_content:
            print("✅ 'localhost' found in hosts file")
        else:
            print("⚠️ 'localhost' not found in hosts file - this might cause issues")
    except:
        print("⚠️ Could not read hosts file")

def main():
    print("=" * 60)
    print("Chrome Hearts Database Connection Checker")
    print("=" * 60)
    
    # Get the port from command line or use default
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}. Using default port 5000.")
    
    # Check if port is open
    port_open = check_port(port)
    
    # Check server processes
    check_server_running()
    
    # Check localhost configuration
    check_localhost_config()
    
    # Test connections
    base_url = f"http://localhost:{port}"
    api_url = f"{base_url}/api/debug"
    ui_url = f"{base_url}/static/index.html"
    
    print("\nTesting API endpoint...")
    api_works = test_connection(api_url)
    
    print("\nTesting UI endpoint...")
    ui_works = test_connection(ui_url)
    
    # Print summary and recommendations
    print("\n" + "=" * 60)
    print("DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    if not port_open:
        print("❌ The server does not appear to be running on port", port)
        print("   Recommendations:")
        print("   1. Make sure you've started the Flask server with 'python app.py'")
        print("   2. Check for error messages when starting the server")
        print("   3. Try running the server with a different port: python app.py")
    elif not (api_works or ui_works):
        print("⚠️ The server is running, but connections are failing")
        print("   Recommendations:")
        print("   1. Check if your firewall is blocking connections to localhost")
        print("   2. Try accessing with the IP address instead: http://127.0.0.1:" + str(port))
        print("   3. Restart your browser and try again")
        print("   4. Check if your antivirus or security software is blocking connections")
    else:
        print("✅ Some connections are working!")
        
        if api_works and not ui_works:
            print("   The API is accessible but the UI is not.")
            print("   Try accessing the UI directly: http://localhost:" + str(port) + "/static/index.html")
        elif ui_works and not api_works:
            print("   The UI is accessible but the API is not.")
            print("   There might be an issue with the API implementation.")
    
    print("\nFor more advanced troubleshooting:")
    print("1. Check the Flask server logs for error messages")
    print("2. Try restarting your computer to release any locked ports")
    print("3. Make sure you have all required packages installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()

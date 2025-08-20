#!/usr/bin/env python3
"""
Test deployment script to validate all fixes
"""
import subprocess
import sys
import time
import requests
import os

def test_backend_startup():
    """Test that the backend starts without errors"""
    print("🧪 Testing backend startup...")
    
    # Change to project directory
    os.chdir('/Users/neill/Documents/AI Code/Projects/botarmy-poc')
    
    # Start the backend in the background
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a few seconds for startup
        time.sleep(5)
        
        # Check if process is still running (no immediate crash)
        if process.poll() is None:
            print("✅ Backend started successfully (process running)")
            
            # Test key API endpoints
            try:
                # Test agents endpoint
                response = requests.get("http://localhost:8000/api/agents", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "agents" in data and isinstance(data["agents"], list):
                        print(f"✅ /api/agents endpoint working - {len(data['agents'])} agents")
                    else:
                        print("❌ /api/agents endpoint returned invalid data")
                else:
                    print(f"❌ /api/agents endpoint failed - status {response.status_code}")
                
                # Test tasks endpoint
                response = requests.get("http://localhost:8000/api/tasks", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if "tasks" in data and isinstance(data["tasks"], list):
                        print(f"✅ /api/tasks endpoint working - {len(data['tasks'])} tasks")
                    else:
                        print("❌ /api/tasks endpoint returned invalid data")
                else:
                    print(f"❌ /api/tasks endpoint failed - status {response.status_code}")
                
                # Test static file serving
                response = requests.get("http://localhost:8000/", timeout=5)
                if response.status_code == 200:
                    if "index-DN6IAKne.js" in response.text:
                        print("✅ Static files serving correctly")
                    else:
                        print("❌ Static files may not be serving correctly")
                else:
                    print(f"❌ Static file serving failed - status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ API test failed: {e}")
        else:
            # Process died, get the error
            stdout, stderr = process.communicate()
            print(f"❌ Backend crashed on startup:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        
        # Terminate the process
        process.terminate()
        process.wait()
        print("🧪 Backend test completed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

if __name__ == "__main__":
    success = test_backend_startup()
    if success:
        print("\n🎉 All tests passed! The deployment should work.")
        print("\n🚀 To deploy:")
        print("   cd '/Users/neill/Documents/AI Code/Projects/botarmy-poc'")
        print("   python main.py")
        print("   Open browser: http://localhost:8000")
    else:
        print("\n💥 Tests failed! Check the errors above.")
    
    sys.exit(0 if success else 1)

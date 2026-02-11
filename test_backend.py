"""
Backend Health Check Script
Tests if the VoicePulse AI backend is running and responsive
"""

import requests
import sys

def check_backend():
    """Check if backend server is running"""
    
    backend_url = "http://localhost:5000"
    
    print("=" * 60)
    print("VoicePulse AI - Backend Health Check")
    print("=" * 60)
    print()
    
    try:
        print(f"Testing connection to: {backend_url}")
        print("Sending health check request...")
        
        response = requests.get(f"{backend_url}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print()
            print("✅ SUCCESS! Backend is running!")
            print()
            print("Server Details:")
            print(f"  Status: {data.get('status', 'unknown')}")
            print(f"  Service: {data.get('service', 'unknown')}")
            print(f"  Timestamp: {data.get('timestamp', 'unknown')}")
            print()
            print("=" * 60)
            print("🎉 Your VoicePulse AI backend is ready to use!")
            print("=" * 60)
            print()
            print("Next steps:")
            print("1. Open frontend/index.html in your browser")
            print("2. Upload or record audio")
            print("3. Click 'Analyze Emotion'")
            print()
            return True
        else:
            print(f"❌ ERROR: Server returned status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print()
        print("❌ ERROR: Cannot connect to backend server")
        print()
        print("The server is not running. Please start it:")
        print("  cd backend")
        print("  python app.py")
        print()
        return False
        
    except requests.exceptions.Timeout:
        print()
        print("❌ ERROR: Connection timeout")
        print("Server is not responding")
        print()
        return False
        
    except Exception as e:
        print()
        print(f"❌ ERROR: {str(e)}")
        print()
        return False

if __name__ == "__main__":
    success = check_backend()
    sys.exit(0 if success else 1)

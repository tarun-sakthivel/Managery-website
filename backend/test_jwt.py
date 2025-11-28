import requests
import json
import jwt

# Test login and check JWT token contents
def test_jwt_token():
    url = "http://localhost:8000/auth/token"
    
    # Replace with actual test credentials
    data = {
        "username": "pugazh@example.com",  # or whatever email you're using
        "password": "your_password_here"     # replace with actual password
    }
    
    print("Testing JWT token from backend...")
    print(f"URL: {url}")
    print(f"Username: {data['username']}")
    print()
    
    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            print(f"\n✅ Login successful!")
            print(f"Token (first 50 chars): {access_token[:50]}...")
            
            # Decode JWT without verification to see contents
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            
            print(f"\n📋 JWT Token Contents:")
            print(json.dumps(decoded, indent=2))
            
            # Check for name and department
            has_name = "name" in decoded
            has_department = "department" in decoded
            
            print(f"\n🔍 Verification:")
            print(f"  - Has 'name' field: {'✅ YES' if has_name else '❌ NO'}")
            print(f"  - Has 'department' field: {'✅ YES' if has_department else '❌ NO'}")
            
            if has_name and has_department:
                print(f"\n✅ Backend is working correctly!")
                print(f"   Name: {decoded.get('name')}")
                print(f"   Department: {decoded.get('department')}")
            else:
                print(f"\n❌ Backend NOT updated - name/department missing from JWT!")
                print(f"   You need to restart the backend server.")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("="*60)
    print("JWT TOKEN VERIFICATION SCRIPT")
    print("="*60)
    print()
    print("IMPORTANT: Edit this script and replace:")
    print('  - "your_password_here" with your actual password')
    print('  - "pugazh@example.com" with your actual email if different')
    print()
    print("="*60)
    print()
    
    test_jwt_token()

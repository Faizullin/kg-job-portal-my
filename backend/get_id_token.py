#!/usr/bin/env python3
"""
Script to get Firebase ID token for a user by email
Usage: python get_id_token.py <email>
"""

import requests
import sys
import json

def get_firebase_id_token(email):
    """
    Get Firebase ID token for a user by email
    This demonstrates the complete flow:
    1. Get custom token from debug endpoint
    2. Show how to convert it to ID token (requires Firebase client SDK)
    """
    
    print(f"🔍 Getting Firebase user info for: {email}")
    
    # Step 1: Get custom token from debug endpoint
    debug_url = "http://localhost:8000/api/v1/debug/firebase-token/"
    
    try:
        response = requests.post(debug_url, json={"email": email})
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ User found!")
            print(f"📧 Email: {data['email']}")
            print(f"🆔 Firebase UID: {data['firebase_user_id']}")
            print(f"👤 Display Name: {data['display_name']}")
            
            print(f"\n🔑 Custom Token:")
            print(f"{data['custom_token']}")
            
            print(f"\n📋 To get ID token, you need to:")
            print(f"1. Use Firebase client SDK in browser/JavaScript")
            print(f"2. Call: firebase.auth().signInWithCustomToken(customToken)")
            print(f"3. Get ID token: userCredential.user.getIdToken()")
            
            print(f"\n🌐 Or use the HTML debug tool:")
            print(f"Open: http://localhost:8000/get_firebase_id_token.html")
            
            # Test the custom token by trying to authenticate
            print(f"\n🧪 Testing authentication with custom token...")
            auth_url = "http://localhost:8000/api/v1/auth/firebase/"
            
            # Note: This will fail because we need ID token, not custom token
            # But it shows the endpoint structure
            print(f"⚠️  Note: Custom token cannot be used directly for authentication")
            print(f"   You need to convert it to ID token first using Firebase client SDK")
            
            return data['custom_token']
            
        else:
            error_data = response.json()
            print(f"❌ Error: {error_data.get('error', 'Unknown error')}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure Django server is running on localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def show_usage():
    """Show usage instructions"""
    print("Firebase ID Token Debug Tool")
    print("=" * 40)
    print("Usage: python get_id_token.py <email>")
    print("Example: python get_id_token.py user@example.com")
    print()
    print("This script will:")
    print("1. Get Firebase user info by email")
    print("2. Return a custom token")
    print("3. Show instructions to convert to ID token")
    print()
    print("For direct ID token conversion, use the HTML tool:")
    print("http://localhost:8000/get_firebase_id_token.html")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        show_usage()
        sys.exit(1)
    
    email = sys.argv[1]
    get_firebase_id_token(email)

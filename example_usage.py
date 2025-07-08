#!/usr/bin/env python3
"""
Example: How other applications can use the Secure Token Client
"""

from token_client import SecureTokenClient, get_token_for_application
import requests

def example_github_integration():
    """Example: Using token for GitHub API integration"""
    print("🔗 GitHub Integration Example")
    print("=" * 40)
    
    # Get token for GitHub integration
    token = get_token_for_application(
        api_url="http://localhost:8000",
        username="testuser",
        password="testpass123",
        user_id="testuser",
        application_name="github-integration",
        purpose="GitHub API access"
    )
    
    if token:
        print(f"✅ Token retrieved: {token[:10]}...")
        
        # Use token with GitHub API
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            # Example: Get user info from GitHub
            response = requests.get("https://api.github.com/user", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ GitHub API access successful")
                print(f"   User: {user_data.get('login', 'Unknown')}")
                print(f"   Name: {user_data.get('name', 'Unknown')}")
            else:
                print(f"❌ GitHub API error: {response.status_code}")
        except Exception as e:
            print(f"❌ GitHub API request failed: {e}")
    else:
        print("❌ Failed to retrieve token")

def example_custom_api_integration():
    """Example: Using token for custom API integration"""
    print("\n🔗 Custom API Integration Example")
    print("=" * 40)
    
    # Initialize client
    client = SecureTokenClient("http://localhost:8000")
    
    # Login
    if client.login("testuser", "testpass123"):
        print("✅ Login successful")
        
        # Get token
        token_data = client.get_token(
            user_id="testuser",
            application_name="custom-api-client",
            purpose="External service authentication"
        )
        
        if token_data:
            token = token_data["token"]
            print(f"✅ Token retrieved: {token[:10]}...")
            
            # Use token with custom API
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Example API call
            try:
                response = requests.post(
                    "https://api.example.com/data",
                    headers=headers,
                    json={"action": "fetch_data"}
                )
                print(f"✅ Custom API call successful: {response.status_code}")
            except Exception as e:
                print(f"❌ Custom API call failed: {e}")
        else:
            print("❌ Failed to retrieve token")
    else:
        print("❌ Login failed")

def example_token_management():
    """Example: Token management operations"""
    print("\n🔧 Token Management Example")
    print("=" * 40)
    
    client = SecureTokenClient("http://localhost:8000")
    
    if client.login("testuser", "testpass123"):
        # Check token status
        status = client.check_token_status("testuser")
        if status:
            print(f"✅ Token status: {status}")
        
        # Health check
        if client.health_check():
            print("✅ API server is healthy")
        else:
            print("❌ API server is not responding")

def example_error_handling():
    """Example: Error handling scenarios"""
    print("\n⚠️ Error Handling Example")
    print("=" * 40)
    
    client = SecureTokenClient("http://localhost:8000")
    
    # Try to access token without login
    try:
        client.get_token("testuser", "test-app", "testing")
    except ValueError as e:
        print(f"✅ Caught expected error: {e}")
    
    # Try with wrong credentials
    if not client.login("wronguser", "wrongpass"):
        print("✅ Correctly rejected wrong credentials")
    
    # Try to access another user's token
    if client.login("testuser", "testpass123"):
        token_data = client.get_token(
            user_id="otheruser",  # Different user
            application_name="test-app",
            purpose="testing"
        )
        if not token_data:
            print("✅ Correctly denied access to other user's token")

if __name__ == "__main__":
    print("🚀 Secure Token Client Examples")
    print("=" * 50)
    
    # Run examples
    example_github_integration()
    example_custom_api_integration()
    example_token_management()
    example_error_handling()
    
    print("\n" + "=" * 50)
    print("✅ All examples completed!") 
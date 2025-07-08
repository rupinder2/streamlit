#!/usr/bin/env python3
"""
Secure Token Client Library
Python client for accessing tokens from the Secure Token API
"""

import requests
import json
from typing import Optional, Dict, Any
from datetime import datetime
import os

class SecureTokenClient:
    """Client for accessing secure tokens via API"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        """
        Initialize the token client
        
        Args:
            api_base_url: Base URL of the token API server
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.access_token = None
        self.session = requests.Session()
    
    def login(self, username: str, password: str) -> bool:
        """
        Authenticate with the token API
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            response = self.session.post(
                f"{self.api_base_url}/auth/login",
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                return True
            else:
                print(f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Login error: {e}")
            return False
    
    def get_token(self, user_id: str, application_name: str, purpose: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a token for external application use
        
        Args:
            user_id: ID of the user whose token to access
            application_name: Name of the application requesting the token
            purpose: Purpose for which the token is being used
            
        Returns:
            dict: Token data including the actual token, or None if failed
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call login() first.")
        
        try:
            response = self.session.post(
                f"{self.api_base_url}/tokens/access",
                json={
                    "user_id": user_id,
                    "application_name": application_name,
                    "purpose": purpose
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Token access failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Token access error: {e}")
            return None
    
    def check_token_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if a user has a token (without revealing the token)
        
        Args:
            user_id: ID of the user to check
            
        Returns:
            dict: Token status information, or None if failed
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call login() first.")
        
        try:
            response = self.session.get(
                f"{self.api_base_url}/tokens/status/{user_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Status check failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Status check error: {e}")
            return None
    
    def delete_token(self, user_id: str) -> bool:
        """
        Delete a user's token
        
        Args:
            user_id: ID of the user whose token to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call login() first.")
        
        try:
            response = self.session.delete(
                f"{self.api_base_url}/tokens/{user_id}"
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"Token deletion failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Token deletion error: {e}")
            return False
    
    def health_check(self) -> bool:
        """
        Check if the API server is healthy
        
        Returns:
            bool: True if server is healthy, False otherwise
        """
        try:
            response = self.session.get(f"{self.api_base_url}/health")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

# Example usage and utility functions
def get_token_for_application(
    api_url: str,
    username: str,
    password: str,
    user_id: str,
    application_name: str,
    purpose: str
) -> Optional[str]:
    """
    Convenience function to get a token for an application
    
    Args:
        api_url: Base URL of the token API
        username: User's username
        password: User's password
        user_id: ID of the user whose token to access
        application_name: Name of the application
        purpose: Purpose for using the token
        
    Returns:
        str: The token if successful, None otherwise
    """
    client = SecureTokenClient(api_url)
    
    if client.login(username, password):
        token_data = client.get_token(user_id, application_name, purpose)
        if token_data:
            return token_data["token"]
    
    return None

# Example usage
if __name__ == "__main__":
    # Example: How another application would use this client
    
    # Initialize client
    client = SecureTokenClient("http://localhost:8000")
    
    # Login
    if client.login("testuser", "testpass123"):
        print("✅ Login successful")
        
        # Get token for an application
        token_data = client.get_token(
            user_id="testuser",
            application_name="my-external-app",
            purpose="API integration"
        )
        
        if token_data:
            print(f"✅ Token retrieved: {token_data['token'][:10]}...")
            print(f"   Generated: {token_data['generation_method']}")
            print(f"   Created: {token_data['created_at']}")
        else:
            print("❌ Failed to retrieve token")
        
        # Check token status
        status = client.check_token_status("testuser")
        if status:
            print(f"✅ Token status: {status}")
    else:
        print("❌ Login failed") 
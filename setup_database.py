#!/usr/bin/env python3
"""
Database setup script for secure token storage
"""

import os
import hashlib
from dotenv import load_dotenv
from database import SecureTokenStorage

def hash_password(password):
    """Hash password for secure storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def setup_database():
    """Initialize database and create test user"""
    print("Setting up secure token storage database...")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize token storage
    token_storage = SecureTokenStorage()
    
    # Test database connection
    conn = token_storage.get_connection()
    if not conn:
        print("❌ Failed to connect to database. Please check your .env configuration.")
        return False
    
    print("✅ Database connection successful")
    conn.close()
    
    # Create test user
    test_username = "testuser"
    test_password = "testpass123"
    password_hash = hash_password(test_password)
    
    if token_storage.create_user(test_username, password_hash):
        print(f"✅ Created test user: {test_username}")
        print(f"   Username: {test_username}")
        print(f"   Password: {test_password}")
        print("   Use these credentials to test the application")
    else:
        print(f"⚠️  Test user {test_username} already exists or creation failed")
    
    print("\n🎉 Database setup complete!")
    print("\nNext steps:")
    print("1. Make sure your .env file is configured with database credentials")
    print("2. Run the Streamlit app: streamlit run app.py")
    print("3. Login with the test credentials above")
    
    return True

if __name__ == "__main__":
    setup_database() 
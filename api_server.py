#!/usr/bin/env python3
"""
Secure Token API Server
Provides secure access to stored tokens for external applications
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
import os
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from database import SecureTokenStorage

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Secure Token API",
    description="API for secure token access",
    version="1.0.0"
)

# Initialize token storage
token_storage = SecureTokenStorage()

# Security
security = HTTPBearer()
JWT_SECRET = os.getenv('JWT_SECRET', 'your-jwt-secret-key-change-this')
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

# Pydantic models
class TokenRequest(BaseModel):
    user_id: str
    application_name: str
    purpose: str

class TokenResponse(BaseModel):
    token: str
    generation_method: str
    created_at: str
    accessed_at: str

class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

def hash_password(password: str) -> str:
    """Hash password for verification"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_jwt_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return username

@app.post("/auth/login", response_model=AuthResponse)
async def login(auth_request: AuthRequest):
    """Authenticate user and return JWT token"""
    # Verify user credentials
    password_hash = hash_password(auth_request.password)
    if not token_storage.verify_user(auth_request.username, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create JWT token
    access_token = create_jwt_token(
        data={"sub": auth_request.username},
        expires_delta=timedelta(hours=JWT_EXPIRY_HOURS)
    )
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRY_HOURS * 3600
    )

@app.post("/tokens/access", response_model=TokenResponse)
async def access_token(
    token_request: TokenRequest,
    current_user: str = Depends(get_current_user)
):
    """Access token for external application"""
    
    # Verify user has access to the requested token
    if current_user != token_request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this token"
        )
    
    # Get token from database
    token_data = token_storage.get_token(token_request.user_id)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found for this user"
        )
    
    # Log access (you might want to add this to database)
    print(f"Token accessed by {current_user} for application: {token_request.application_name}")
    print(f"Purpose: {token_request.purpose}")
    print(f"Access time: {datetime.now().isoformat()}")
    
    return TokenResponse(
        token=token_data['token'],
        generation_method=token_data['generation_method'],
        created_at=token_data['created_at'],
        accessed_at=datetime.now().isoformat()
    )

@app.get("/tokens/status/{user_id}")
async def token_status(
    user_id: str,
    current_user: str = Depends(get_current_user)
):
    """Check if user has a token (without revealing the token)"""
    
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    token_data = token_storage.get_token(user_id)
    if token_data:
        return {
            "has_token": True,
            "generation_method": token_data['generation_method'],
            "created_at": token_data['created_at'],
            "updated_at": token_data['updated_at']
        }
    else:
        return {"has_token": False}

@app.delete("/tokens/{user_id}")
async def delete_token(
    user_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete user's token"""
    
    if current_user != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    success = token_storage.delete_token(user_id)
    if success:
        return {"message": "Token deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 
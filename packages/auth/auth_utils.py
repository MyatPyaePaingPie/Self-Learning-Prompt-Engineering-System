"""
Authentication utilities for bcrypt password hashing and JWT tokens
"""

import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from pydantic import BaseModel

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")  # Use environment variable in production!
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24  # Tokens expire after 24 hours

class TokenData(BaseModel):
    """Structure of JWT token payload"""
    user_id: str
    username: str
    exp: datetime

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    # Convert string to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string for database storage
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password to verify
        hashed: Stored password hash
        
    Returns:
        True if password matches, False otherwise
    """
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_jwt_token(user_id: str, username: str) -> str:
    """
    Create a JWT token for a user
    
    Args:
        user_id: User's UUID as string
        username: User's username
        
    Returns:
        JWT token string
    """
    # Create expiration time
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    # Create payload
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expiration,
        "iat": datetime.utcnow()  # Issued at time
    }
    
    # Create token
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def verify_jwt_token(token: str) -> Optional[TokenData]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData if valid, None if invalid or expired
    """
    try:
        # Decode token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Extract data
        return TokenData(
            user_id=payload["user_id"],
            username=payload["username"],
            exp=datetime.fromtimestamp(payload["exp"])
        )
    
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None

def extract_token_from_header(authorization: str) -> Optional[str]:
    """
    Extract JWT token from Authorization header
    
    Args:
        authorization: Authorization header value (e.g., "Bearer abc123...")
        
    Returns:
        Token string if valid format, None otherwise
    """
    if not authorization:
        return None
    
    # Check if header starts with "Bearer "
    if not authorization.startswith("Bearer "):
        return None
    
    # Extract token (remove "Bearer " prefix)
    token = authorization[7:]  # "Bearer " is 7 characters
    return token if token else None

# Example usage and testing functions
if __name__ == "__main__":
    # Test password hashing
    print("=== Password Hashing Test ===")
    password = "mypassword123"
    hashed = hash_password(password)
    print(f"Original: {password}")
    print(f"Hashed: {hashed}")
    print(f"Verification: {verify_password(password, hashed)}")
    print(f"Wrong password: {verify_password('wrongpassword', hashed)}")
    
    # Test JWT tokens
    print("\n=== JWT Token Test ===")
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    username = "testuser"
    
    token = create_jwt_token(user_id, username)
    print(f"Generated token: {token}")
    
    decoded = verify_jwt_token(token)
    if decoded:
        print(f"Decoded user_id: {decoded.user_id}")
        print(f"Decoded username: {decoded.username}")
        print(f"Expires at: {decoded.exp}")
    else:
        print("Failed to decode token")
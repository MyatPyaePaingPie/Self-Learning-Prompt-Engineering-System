# 🔒 Security Guide: Authentication System Best Practices

## Overview

This authentication system implements production-ready security practices for a Streamlit frontend + FastAPI backend architecture. Here's what makes it secure and how to avoid common pitfalls.

## 🛡️ Security Features Implemented

### 1. Password Security
- **BCrypt Hashing**: Uses bcrypt with automatic salt generation
- **Password Strength**: Frontend validates minimum 6 characters (implement stronger rules in production)
- **No Plain Text Storage**: Passwords are immediately hashed and never stored in plain text

### 2. Token-Based Authentication
- **JWT (JSON Web Tokens)**: Stateless authentication with configurable expiration
- **Bearer Token Scheme**: Industry-standard HTTP Authorization header
- **Token Validation**: Every request validates token signature and expiration

### 3. API Security
- **Protected Routes**: Authentication middleware on sensitive endpoints
- **CORS Configuration**: Properly configured cross-origin resource sharing
- **Input Validation**: Pydantic models validate all request data
- **Error Handling**: Secure error messages that don't leak sensitive information

### 4. Data Encryption
- **HTTPS Ready**: Application configured for TLS/SSL encryption in transit
- **Environment Variables**: Sensitive configuration stored in `.env` files
- **Secret Key Management**: JWT signing key kept separate from code

## ⚠️ Common Security Pitfalls to Avoid

### 1. **Weak Secret Keys**
```python
# ❌ BAD: Weak or hardcoded secrets
SECRET_KEY = "secret123"
SECRET_KEY = "your-secret-key"

# ✅ GOOD: Strong, randomly generated secrets
SECRET_KEY = "your-super-secure-secret-key-change-this-in-production-make-it-at-least-32-characters"
```

### 2. **Password Storage Mistakes**
```python
# ❌ BAD: Storing plain text passwords
user.password = "user_password"

# ❌ BAD: Using weak hashing
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()

# ✅ GOOD: Using bcrypt with salt
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash(password)
```

### 3. **Token Security Issues**
```python
# ❌ BAD: Tokens that never expire
token = jwt.encode({"user": username}, SECRET_KEY)

# ❌ BAD: Storing tokens in localStorage (XSS vulnerable)
localStorage.setItem('token', token)

# ✅ GOOD: Tokens with expiration
token = jwt.encode({
    "sub": username,
    "exp": datetime.utcnow() + timedelta(minutes=30)
}, SECRET_KEY)
```

### 4. **API Security Mistakes**
```python
# ❌ BAD: No authentication on sensitive routes
@app.get("/user_data")
async def get_user_data():
    return {"sensitive": "data"}

# ✅ GOOD: Protected routes with authentication
@app.get("/user_data")
async def get_user_data(current_user: User = Depends(get_current_user)):
    return {"user": current_user.username}
```

### 5. **Error Information Leakage**
```python
# ❌ BAD: Detailed error messages
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# ✅ GOOD: Generic error messages
except Exception as e:
    logger.error(f"Authentication error: {str(e)}")
    raise HTTPException(status_code=401, detail="Authentication failed")
```

## 🔧 Production Deployment Checklist

### Environment Variables (.env)
```bash
# Generate a strong secret key (32+ characters)
SECRET_KEY=your-production-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database URL
DATABASE_URL=postgresql://user:pass@localhost/dbname

# CORS origins (production domains only)
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

### HTTPS Configuration
```python
# FastAPI with HTTPS
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=443,
        ssl_keyfile="/path/to/key.pem",
        ssl_certfile="/path/to/cert.pem"
    )
```

### Database Security
```python
# Use environment variables for database credentials
DATABASE_URL = os.getenv("DATABASE_URL")

# Example for PostgreSQL
DATABASE_URL = "postgresql://username:password@localhost:5432/dbname"
```

## 🧪 Security Testing

### 1. Test Password Hashing
```python
def test_password_hashing():
    password = "test_password"
    hashed = get_password_hash(password)
    
    # Verify hash is different from password
    assert hashed != password
    
    # Verify password verification works
    assert verify_password(password, hashed) == True
    assert verify_password("wrong_password", hashed) == False
```

### 2. Test Token Validation
```python
def test_token_validation():
    # Create token
    token_data = {"sub": "testuser"}
    token = create_access_token(data=token_data)
    
    # Verify token
    decoded = verify_token(token)
    assert decoded.username == "testuser"
    
    # Test expired token
    expired_token = create_access_token(
        data=token_data, 
        expires_delta=timedelta(seconds=-1)
    )
    assert verify_token(expired_token) is None
```

### 3. Test API Security
```python
def test_protected_route_without_token():
    response = client.get("/protected")
    assert response.status_code == 401

def test_protected_route_with_invalid_token():
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 401
```

## 🛠️ Additional Security Enhancements

### 1. Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/login")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(request: Request, ...):
    # Login logic
```

### 2. Password Strength Validation
```python
import re

def validate_password_strength(password: str) -> bool:
    """Validate password meets security requirements."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True
```

### 3. Security Headers
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

## 📚 Additional Resources

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [JWT Security Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Cryptography Documentation](https://cryptography.io/en/latest/)
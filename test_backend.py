#!/usr/bin/env python3
"""
Simple backend test to debug authentication issues
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing imports...")
    
    # Test auth utils
    from packages.auth.auth_utils import hash_password, verify_password, create_jwt_token
    print("✅ Auth utils imported")
    
    # Test database
    from packages.db.session import get_session
    from packages.db.models import User
    print("✅ Database imports successful")
    
    # Test password hashing
    password = "testpass123"
    hashed = hash_password(password)
    verified = verify_password(password, hashed)
    print(f"✅ Password hashing works: {verified}")
    
    # Test JWT
    token = create_jwt_token("test-user-id", "testuser")
    print(f"✅ JWT token generated: {token[:50]}...")
    
    # Test database connection
    with get_session() as session:
        print("✅ Database connection works")
    
    print("\n🎉 All core components working - backend should start properly")
    print("\nTo start backend correctly, run:")
    print("PYTHONPATH=. python3 -m uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
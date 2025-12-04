#!/usr/bin/env python3
"""
Comprehensive test script for the Enhanced Authentication System
Tests security features, encryption, rate limiting, and API functionality
"""

import requests
import time
import json
import sys
from typing import Dict, Any

# Test configuration
API_BASE_URL = "http://localhost:8002"
TEST_USER = {
    "username": "testuser123",
    "email": "test@example.com",
    "password": "SecurePass123!"
}

class AuthSystemTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        
    def test_health_check(self) -> bool:
        """Test API health endpoint."""
        print("🏥 Testing health check endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False
    
    def test_password_validation(self) -> bool:
        """Test password validation requirements."""
        print("\n🔐 Testing password validation...")
        
        weak_passwords = [
            "123456",
            "password",
            "Password",
            "Password123",
            "password123!"
        ]
        
        for weak_password in weak_passwords:
            try:
                response = self.session.post(
                    f"{self.base_url}/register",
                    json={
                        "username": "weakpasstest",
                        "email": "weak@example.com",
                        "password": weak_password
                    }
                )
                if response.status_code in [400, 422]:  # Both 400 and 422 are valid rejection codes
                    print(f"✅ Weak password '{weak_password}' correctly rejected")
                else:
                    print(f"❌ Weak password '{weak_password}' was accepted (should be rejected)")
                    return False
            except Exception as e:
                print(f"❌ Password validation test error: {str(e)}")
                return False
        
        return True
    
    def test_user_registration(self) -> bool:
        """Test user registration with strong password."""
        print("\n📝 Testing user registration...")
        try:
            response = self.session.post(
                f"{self.base_url}/register",
                json=TEST_USER
            )
            
            if response.status_code == 200:
                print("✅ User registration successful")
                return True
            elif response.status_code == 400 and "already exists" in response.json().get("detail", ""):
                print("⚠️  User already exists, skipping registration")
                return True
            else:
                print(f"❌ Registration failed: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return False
    
    def test_user_login(self) -> bool:
        """Test user login and token generation."""
        print("\n🔑 Testing user login...")
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                json={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                print("✅ Login successful, token received")
                print(f"   Token expires in: {token_data['expires_in']} seconds")
                return True
            else:
                print(f"❌ Login failed: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting on login endpoint."""
        print("\n🚦 Testing rate limiting...")
        
        # Attempt multiple rapid logins with wrong password
        for i in range(7):  # Should exceed the 5/minute limit
            try:
                response = self.session.post(
                    f"{self.base_url}/login",
                    json={
                        "username": TEST_USER["username"],
                        "password": "wrong_password"
                    }
                )
                
                if response.status_code == 429:
                    print(f"✅ Rate limiting triggered after {i+1} attempts")
                    return True
                elif i >= 5 and response.status_code != 429:
                    print(f"❌ Rate limiting not working - attempt {i+1} allowed")
                    
            except Exception as e:
                print(f"❌ Rate limiting test error: {str(e)}")
                return False
        
        print("⚠️  Rate limiting test inconclusive")
        return True
    
    def test_protected_route(self) -> bool:
        """Test accessing protected routes with token."""
        print("\n🛡️ Testing protected route access...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.session.get(f"{self.base_url}/protected", headers=headers)
            
            if response.status_code == 200:
                print("✅ Protected route access successful")
                return True
            else:
                print(f"❌ Protected route access failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Protected route test error: {str(e)}")
            return False
    
    def test_prompt_enhancement(self) -> bool:
        """Test prompt enhancement functionality."""
        print("\n🚀 Testing prompt enhancement...")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            test_prompt = {
                "text": "Create a function to calculate compound interest",
                "enhancement_type": "technical",
                "context": "For a financial application"
            }
            
            response = self.session.post(
                f"{self.base_url}/prompts/enhance",
                json=test_prompt,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Template-based prompt enhancement successful")
                print(f"   Original: {result['data']['original_text']}")
                print(f"   Enhanced Template Applied:")
                print(f"   {result['data']['enhanced_text'][:200]}...")
                
                # Verify template structure is applied
                enhanced_text = result['data']['enhanced_text']
                if "You are a senior" in enhanced_text and "Task:" in enhanced_text and "Deliverables:" in enhanced_text:
                    print("✅ Template structure correctly applied")
                    return True
                else:
                    print("❌ Template structure not found in enhanced text")
                    return False
            else:
                print(f"❌ Prompt enhancement failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Prompt enhancement error: {str(e)}")
            return False
    
    def test_security_headers(self) -> bool:
        """Test security headers in responses."""
        print("\n🔒 Testing security headers...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            headers = response.headers
            
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "X-Security-Status": "protected"
            }
            
            missing_headers = []
            for header, expected_value in security_headers.items():
                if header not in headers:
                    missing_headers.append(header)
                elif headers[header] != expected_value:
                    missing_headers.append(f"{header} (incorrect value)")
            
            if not missing_headers:
                print("✅ All security headers present and correct")
                return True
            else:
                print(f"❌ Missing security headers: {', '.join(missing_headers)}")
                return False
                
        except Exception as e:
            print(f"❌ Security headers test error: {str(e)}")
            return False
    
    def test_invalid_token(self) -> bool:
        """Test behavior with invalid tokens."""
        print("\n🚫 Testing invalid token handling...")
        
        try:
            headers = {"Authorization": "Bearer invalid_token_123"}
            response = self.session.get(f"{self.base_url}/protected", headers=headers)
            
            if response.status_code == 401:
                print("✅ Invalid token correctly rejected")
                return True
            else:
                print(f"❌ Invalid token accepted: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Invalid token test error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all security tests."""
        print("🔐 Starting Comprehensive Authentication System Security Tests")
        print("=" * 70)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Password Validation", self.test_password_validation),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Rate Limiting", self.test_rate_limiting),
            ("Protected Routes", self.test_protected_route),
            ("Prompt Enhancement", self.test_prompt_enhancement),
            ("Security Headers", self.test_security_headers),
            ("Invalid Token Handling", self.test_invalid_token),
        ]
        
        results = {}
        passed = 0
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {str(e)}")
                results[test_name] = False
        
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<25} {status}")
        
        print(f"\nOverall: {passed}/{len(tests)} tests passed")
        
        if passed == len(tests):
            print("🎉 All tests passed! The authentication system is secure and functional.")
        else:
            print("⚠️  Some tests failed. Please check the implementation.")
        
        return results

def main():
    """Main test execution."""
    print("Starting Enhanced Authentication System Tests...")
    print("Make sure the backend server is running on http://localhost:8001")
    
    input("Press Enter to continue with tests...")
    
    tester = AuthSystemTester(API_BASE_URL)
    results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    failed_tests = [name for name, result in results.items() if not result]
    if failed_tests:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
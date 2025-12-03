from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Union
import json

class EncryptionManager:
    """Handles application-layer encryption for sensitive data."""
    
    def __init__(self, secret_key: str = None):
        """Initialize encryption with a secret key."""
        if secret_key:
            # Derive key from secret
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"ultra_secure_auth_system_salt_2025_change_in_production_32_bytes",
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
            self.cipher = Fernet(key)
        else:
            # Generate a new key
            self.cipher = Fernet(Fernet.generate_key())
    
    def encrypt(self, data: Union[str, dict]) -> str:
        """Encrypt string or dict data."""
        if isinstance(data, dict):
            data = json.dumps(data)
        
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data back to string."""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception:
            raise ValueError("Invalid encrypted data")
    
    def decrypt_json(self, encrypted_data: str) -> dict:
        """Decrypt data back to dict."""
        decrypted_str = self.decrypt(encrypted_data)
        return json.loads(decrypted_str)

# Global encryption manager instance
encryption_manager = None

def get_encryption_manager() -> EncryptionManager:
    """Get or create the global encryption manager."""
    global encryption_manager
    if encryption_manager is None:
        secret_key = os.getenv("SECRET_KEY")
        encryption_manager = EncryptionManager(secret_key)
    return encryption_manager

def encrypt_sensitive_data(data: Union[str, dict]) -> str:
    """Utility function to encrypt sensitive data."""
    return get_encryption_manager().encrypt(data)

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Utility function to decrypt sensitive data."""
    return get_encryption_manager().decrypt(encrypted_data)
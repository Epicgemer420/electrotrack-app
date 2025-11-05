"""Data encryption utilities for athlete privacy"""

from cryptography.fernet import Fernet
from typing import Dict, Any, Optional
import base64
import os


class EncryptionManager:
    """Manages encryption/decryption of sensitive athlete data"""
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption manager
        
        Args:
            key: Encryption key (if None, generates new key or loads from env)
        """
        if key is None:
            key_str = os.getenv('ELECTROTRACK_ENCRYPTION_KEY')
            if key_str:
                key = base64.urlsafe_b64decode(key_str.encode())
            else:
                # Generate new key (in production, should be stored securely)
                key = Fernet.generate_key()
        
        self.cipher = Fernet(key)
        self.key = key
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def get_key_base64(self) -> str:
        """Get encryption key as base64 string (for storage)"""
        return base64.urlsafe_b64encode(self.key).decode()


# Global encryption manager instance
_encryption_manager = None

def get_encryption_manager() -> EncryptionManager:
    """Get or create global encryption manager"""
    global _encryption_manager
    if _encryption_manager is None:
        _encryption_manager = EncryptionManager()
    return _encryption_manager


def encrypt_data(data: Dict[str, Any], fields: list = ['athlete_id']) -> Dict[str, Any]:
    """
    Encrypt sensitive fields in data dictionary
    
    Args:
        data: Dictionary containing data
        fields: List of field names to encrypt
        
    Returns:
        Dictionary with encrypted fields
    """
    manager = get_encryption_manager()
    encrypted = data.copy()
    
    for field in fields:
        if field in encrypted and encrypted[field]:
            encrypted[field] = manager.encrypt(str(encrypted[field]))
    
    return encrypted


def decrypt_data(data: Dict[str, Any], fields: list = ['athlete_id']) -> Dict[str, Any]:
    """
    Decrypt sensitive fields in data dictionary
    
    Args:
        data: Dictionary with encrypted fields
        fields: List of field names to decrypt
        
    Returns:
        Dictionary with decrypted fields
    """
    manager = get_encryption_manager()
    decrypted = data.copy()
    
    for field in fields:
        if field in decrypted and decrypted[field]:
            try:
                decrypted[field] = manager.decrypt(str(decrypted[field]))
            except Exception:
                # Field might not be encrypted
                pass
    
    return decrypted


"""
Utility for encrypting and decrypting sensitive config files in Proposal AI.
"""
from cryptography.fernet import Fernet
import os

class ConfigEncryptor:
    """Encrypt and decrypt config files using Fernet symmetric encryption."""
    def __init__(self, key_path='config/secret.key'):
        self.key_path = key_path
        self.key = self.load_or_create_key()
        self.cipher = Fernet(self.key)

    def load_or_create_key(self):
        """Load existing key or create a new one."""
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as f:
                return f.read()
        key = Fernet.generate_key()
        with open(self.key_path, 'wb') as f:
            f.write(key)
        return key

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data using Fernet."""
        return self.cipher.encrypt(data)

    def decrypt(self, token: bytes) -> bytes:
        """Decrypt data using Fernet."""
        return self.cipher.decrypt(token)

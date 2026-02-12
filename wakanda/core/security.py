"""
Security management for Wakanda Protocol
Handles encryption, key management, HSM integration, and authentication
"""

import os
import secrets
from typing import Optional, Dict, Any, Union
from datetime import datetime, timedelta
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel

from .config import settings


class TokenData(BaseModel):
    """Token data model"""
    username: Optional[str] = None
    scopes: list[str] = []


class SecurityManager:
    """Central security management class"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._setup_encryption()
        self._setup_hsm()
    
    def _setup_encryption(self):
        """Setup encryption keys and Fernet cipher"""
        if settings.encryption_key:
            self.fernet = Fernet(settings.encryption_key.encode())
        else:
            # Generate a new key if none provided
            key = Fernet.generate_key()
            self.fernet = Fernet(key)
            print(f"WARNING: Generated new encryption key: {key.decode()}")
            print("Store this key securely as WAKANDA_ENCRYPTION_KEY environment variable")
    
    def _setup_hsm(self):
        """Setup HSM integration if enabled"""
        self.hsm_enabled = settings.hsm_enabled
        if self.hsm_enabled:
            try:
                # Placeholder for HSM integration
                # In production, this would use PKCS#11 libraries
                print("HSM integration enabled")
                self._init_hsm()
            except Exception as e:
                print(f"Failed to initialize HSM: {e}")
                self.hsm_enabled = False
    
    def _init_hsm(self):
        """Initialize HSM connection"""
        if not self.hsm_enabled:
            return
        
        # Placeholder for actual HSM initialization
        # This would typically involve:
        # 1. Loading PKCS#11 library
        # 2. Opening session with HSM
        # 3. Authenticating with PIN
        # 4. Getting key handles
        pass
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        
        to_encode.update({"exp": expire})
        
        if self.hsm_enabled:
            # Use HSM for JWT signing in production
            encoded_jwt = self._sign_jwt_with_hsm(to_encode)
        else:
            encoded_jwt = jwt.encode(
                to_encode, 
                settings.secret_key, 
                algorithm=settings.algorithm
            )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode a JWT token"""
        try:
            if self.hsm_enabled:
                payload = self._verify_jwt_with_hsm(token)
            else:
                payload = jwt.decode(
                    token, 
                    settings.secret_key, 
                    algorithms=[settings.algorithm]
                )
            
            username: str = payload.get("sub")
            scopes: list = payload.get("scopes", [])
            
            if username is None:
                return None
            
            return TokenData(username=username, scopes=scopes)
        except JWTError:
            return None
    
    def _sign_jwt_with_hsm(self, payload: dict) -> str:
        """Sign JWT using HSM (placeholder implementation)"""
        # In production, this would use HSM's private key
        # For now, fallback to regular signing
        return jwt.encode(
            payload, 
            settings.secret_key, 
            algorithm=settings.algorithm
        )
    
    def _verify_jwt_with_hsm(self, token: str) -> dict:
        """Verify JWT using HSM (placeholder implementation)"""
        # In production, this would use HSM's public key
        # For now, fallback to regular verification
        return jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
    
    def encrypt_data(self, data: Union[str, bytes]) -> bytes:
        """Encrypt data using Fernet symmetric encryption"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.fernet.encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using Fernet symmetric encryption"""
        return self.fernet.decrypt(encrypted_data)
    
    def generate_api_key(self, length: int = 32) -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(length)
    
    def generate_rsa_keypair(self, key_size: int = 2048) -> tuple[bytes, bytes]:
        """Generate RSA key pair for asymmetric encryption"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for HTTP responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://fastapi.tiangolo.com",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }


# Global security manager instance
security_manager = SecurityManager()
# from datetime import datetime, timedelta, timezone
# from typing import Optional
# from jose import JWTError, jwt
# from passlib.context import CryptContext

# # CONFIGURATION
# SECRET_KEY = "super-secret-key-change-this-in-production"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30
# # Removed MAX_PASSWORD_BYTES = 72 (unnecessary with argon2)

# # CHANGE: Switched to Argon2, the recommended standard
# pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# def verify_password(plain_password, hashed_password):
#     """Verifies a plain-text password against a hashed one."""
#     # Argon2 handles password length and encoding automatically
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     """Hashes a password string using Argon2."""
#     # Argon2 handles password length and encoding automatically
#     return pwd_context.hash(password)

# def create_access_token(data: dict):
#     """Creates a JWT access token."""
#     to_encode = data.copy()
    
#     # Use timezone-aware datetime for UTC
#     expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
    
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# CONFIGURATION
SECRET_KEY = "super-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# CHANGE: Switched to Argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verifies a plain-text password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a password string using Argon2."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates a JWT access token.
    The 'data' dict MUST include 'sub' (email) and 'role'.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
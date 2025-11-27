# # from datetime import datetime, timedelta, timezone
# # from typing import Optional
# # from jose import JWTError, jwt
# # from passlib.context import CryptContext

# # # CONFIGURATION
# # SECRET_KEY = "super-secret-key-change-this-in-production"
# # ALGORITHM = "HS256"
# # ACCESS_TOKEN_EXPIRE_MINUTES = 30
# # # Removed MAX_PASSWORD_BYTES = 72 (unnecessary with argon2)

# # # CHANGE: Switched to Argon2, the recommended standard
# # pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# # def verify_password(plain_password, hashed_password):
# #     """Verifies a plain-text password against a hashed one."""
# #     # Argon2 handles password length and encoding automatically
# #     return pwd_context.verify(plain_password, hashed_password)

# # def get_password_hash(password: str) -> str:
# #     """Hashes a password string using Argon2."""
# #     # Argon2 handles password length and encoding automatically
# #     return pwd_context.hash(password)

# # def create_access_token(data: dict):
# #     """Creates a JWT access token."""
# #     to_encode = data.copy()
    
# #     # Use timezone-aware datetime for UTC
# #     expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
# #     to_encode.update({"exp": expire})
    
# #     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
# #     return encoded_jwt
# # from datetime import datetime, timedelta, timezone
# # from typing import Optional, Dict
# # from jose import JWTError, jwt
# # from passlib.context import CryptContext
# # from pydantic import BaseModel

# # # CONFIGURATION
# # SECRET_KEY = "super-secret-key-change-this-in-production"
# # ALGORITHM = "HS256"
# # ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # # CHANGE: Switched to Argon2
# # pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# # def verify_password(plain_password, hashed_password):
# #     """Verifies a plain-text password against a hashed one."""
# #     return pwd_context.verify(plain_password, hashed_password)

# # def get_password_hash(password: str) -> str:
# #     """Hashes a password string using Argon2."""
# #     return pwd_context.hash(password)

# # def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
# #     """
# #     Creates a JWT access token.
# #     The 'data' dict MUST include 'sub' (email) and 'role'.
# #     """
# #     to_encode = data.copy()
    
# #     if expires_delta:
# #         expire = datetime.now(timezone.utc) + expires_delta
# #     else:
# #         expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
# #     to_encode.update({"exp": expire})
    
# #     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
# #     return encoded_jwt

# from datetime import datetime, timedelta, timezone
# from typing import Optional, Dict
# from jose import JWTError, jwt
# from passlib.context import CryptContext
# from fastapi import Depends, HTTPException
# from fastapi.security import OAuth2PasswordBearer

# from models import EmployeeInDB # Import the model that holds user data

# # CONFIGURATION
# SECRET_KEY = "super-secret-key-change-this-in-production"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # CHANGE: Switched to Argon2 (Best Practice)
# pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token") # Endpoint for token request

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verifies a plain-text password against a hashed one."""
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     """Hashes a password string using Argon2."""
#     return pwd_context.hash(password)

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     """
#     Creates a JWT access token.
#     The 'data' dict MUST include 'sub' (email) and 'role'.
#     """
#     to_encode = data.copy()
    
#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
#     to_encode.update({"exp": expire})
    
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# # Dependency to decode the JWT token and return the payload
# def decode_access_token(token: str) -> Dict:
#     """Decodes the JWT token and handles expiration/decoding errors."""
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
#         # Ensure critical claims exist
#         user_id: str = payload.get("id")
#         email: str = payload.get("sub")
#         role: str = payload.get("role")
        
#         if user_id is None or email is None or role is None:
#             raise credentials_exception
            
#         return {"id": user_id, "sub": email, "role": role}

#     except JWTError:
#         raise credentials_exception

# # Dependency to get the current authenticated user's data
# async def get_current_user_data(token: str = Depends(oauth2_scheme)) -> Dict:
#     """Decodes token and returns user payload (id, email, role)."""
#     return decode_access_token(token)

# # Dependency to require Team Leader role
# async def require_team_leader(user_data: Dict = Depends(get_current_user_data)):
#     """Raises exception if the authenticated user is not a Team Leader."""
#     if user_data.get("role") != "team_leader":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, 
#             detail="Operation requires Team Leader privileges"
#         )
#     return user_data

import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# read from env if present; set safe defaults for local dev
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Expect payload to contain: sub/email, id, role
        user_id = payload.get("id")
        email = payload.get("email") or payload.get("sub")
        role = payload.get("role")
        if user_id is None or email is None or role is None:
            raise credentials_exception
        return {"id": user_id, "email": email, "role": role}
    except JWTError:
        raise credentials_exception

# dependency used by routes
async def get_current_user_data(token: str = Depends(oauth2_scheme)) -> Dict:
    return decode_access_token(token)

async def require_team_leader(user_data: Dict = Depends(get_current_user_data)):
    if user_data.get("role") != "team_leader":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation requires Team Leader privileges")
    return user_data

# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from jose import JWTError, jwt
# from sqlmodel import Session
# from database import get_session
# from models import Employee
# from security import SECRET_KEY, ALGORITHM

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# def get_current_employee(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
        
#     employee = session.query(Employee).filter(Employee.email == email).first()
#     if employee is None:
#         raise credentials_exception
#     return employee
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError, jwt
from typing import Optional
from models import PyObjectId, EmployeeInDB  # Use updated models.py imports

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Token data schema compatible with Pydantic V2
class TokenData(BaseModel):
    username: Optional[str] = None

# Sample secret and algorithm as placeholders
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(oauth2_scheme)) -> EmployeeInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # Retrieve the user from the database using username (email)
    # Here replace with your DB call returning EmployeeInDB object
    user = None  # Implement DB fetch here, returning EmployeeInDB instance
    if user is None:
        raise credentials_exception
    return user

def validate_object_id(id_str: str) -> PyObjectId:
    return PyObjectId.validate(id_str)

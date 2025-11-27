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

from typing import Annotated, Optional ,Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select
from database import get_session
from models import Employee
from security import SECRET_KEY, ALGORITHM

# Dependency used in all protected routes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
SessionDep = Annotated[Session, Depends(get_session)]

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def get_current_user_data(token: str = Depends(oauth2_scheme)) -> Dict:
    """Decodes the token and returns the payload data (email, role)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        email: str = payload.get("sub")
        role: str = payload.get("role")
        user_id: Optional[int] = payload.get("id") # Recommended: include ID in payload
        
        if email is None or role is None:
            raise credentials_exception
            
        return {"email": email, "role": role, "id": user_id}
    except JWTError:
        raise credentials_exception

# Dependency for routes that need the full Employee ORM object
def get_current_employee(user_data: dict = Depends(get_current_user_data), session: Session = Depends(get_session)) -> Employee:
    """Fetches the full Employee ORM object."""
    employee = session.exec(select(Employee).where(Employee.email == user_data["email"])).first()
    if employee is None:
        raise credentials_exception
    return employee

# Dependency for routes that require the Team Leader role
def require_team_leader(user_data: dict = Depends(get_current_user_data)) -> dict:
    """Dependency that ensures the current user is a Team Leader."""
    if user_data.get("role") != "team_leader":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Must be a Team Leader."
        )
    return user_data

CurrentEmployee = Annotated[Employee, Depends(get_current_employee)]
CurrentUserData = Annotated[dict, Depends(get_current_user_data)]
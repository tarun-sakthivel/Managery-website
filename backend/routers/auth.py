# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlmodel import Session, select
# from database import get_session
# from models import Employee
# from security import verify_password, create_access_token

# router = APIRouter(prefix="/auth", tags=["Authentication"])

# @router.post("/login")
# def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
#     # 1. Find user
#     statement = select(Employee).where(Employee.email == form_data.username)
#     employee = session.exec(statement).first()
    
#     # 2. Check password
#     if not employee or not verify_password(form_data.password, employee.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     # 3. Generate Token
#     access_token = create_access_token(data={"sub": employee.email})
#     return {"access_token": access_token, "token_type": "bearer"}

# class CreateUserRequest(BaseModel):
#     username: str
#     email: EmailStr
#     password: str
#     # Add an optional role field for registration
#     role: Optional[str] = "employee" # Default new users to 'employee'

#     # ... (rest of imports)

# # ... (other code)

# def authenticate_user(email: str, password: str, db: Session):
#     # ... (code to fetch user)
#     user = db.query(User).filter(User.email == email).first()
#     if not user or not bcrypt_context.verify(password, user.hashed_password):
#         raise HTTPException(status_code=400, detail="Invalid credentials")
#     return user # <-- Returns the User/Employee ORM object

# def create_access_token(email: str, user_email: str, role: str, expires_delta: timedelta = timedelta(minutes=260)):
#     # ADDED 'role: str' to parameters
#     encode = {"sub": email, "email": user_email, "role": role} # <-- ADD ROLE TO PAYLOAD
#     expires = datetime.now(timezone.utc) + expires_delta
#     encode.update({"exp": expires}) 
#     return jwt.encode(encode, secret_key, algorithm=algorithm)

# def get_current_user(token: str = Depends(OAuth2_Bearer)):
#     try:
#         payload = jwt.decode(token, secret_key, algorithms=[algorithm])
#         email: str = payload.get("sub")
#         user_email: str = payload.get("email")
#         role: str = payload.get("role") # <-- EXTRACT THE ROLE
        
#         if email is None or user_email is None or role is None:
#             raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
#         # Return the extracted user data, including the role
#         return {"email": email, "user_email": user_email, "role": role}
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# # ----------------------------------------------------------------------
# # NEW DEPENDENCY FUNCTION TO ENFORCE TEAM LEADER ACCESS
# # ----------------------------------------------------------------------

# # NOTE: Use 'get_current_user' as the dependency, since it extracts the role
# CurrentActiveUser = Annotated[dict, Depends(get_current_user)] 

# def require_team_leader(user_data: CurrentActiveUser):
#     """Dependency that ensures the current user is a Team Leader."""
#     if user_data.get("role") != "team_leader":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Access denied. Must be a Team Leader."
#         )
#     return user_data # Return the user data if successful

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from database import get_session
from models import Employee
from schemas import Token, EmployeeCreate
from security import verify_password, create_access_token, get_password_hash
from datetime import timedelta
from dependencies import SessionDep

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=201)
def register_employee(employee: EmployeeCreate, session: SessionDep):
    """Endpoint for new employee registration (creates an 'employee' role by default)."""
    
    # 1. Validate Role (only allow 'employee' for self-registration)
    if employee.role.lower() not in ["employee", "team_leader"]: # Allowing TL creation for initial setup
        raise HTTPException(status_code=400, detail="Invalid role specified.")

    # 2. Check for existing user
    if session.exec(select(Employee).where(Employee.email == employee.email)).first():
        raise HTTPException(status_code=400, detail="Employee with this email already exists")

    # 3. Hash password and create user
    hashed_pwd = get_password_hash(employee.password)
    
    # Ensure the role is correctly set
    db_employee = Employee.model_validate(employee, update={"hashed_password": hashed_pwd, "role": employee.role.lower()})
    
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)

    # 4. Generate Token (Log user in immediately)
    access_token = create_access_token(
        data={"sub": db_employee.email, "role": db_employee.role, "id": db_employee.id},
        expires_delta=timedelta(minutes=500)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login( session: SessionDep,form_data: OAuth2PasswordRequestForm = Depends()):
    """Logs in an employee and returns an access token."""
    
    # 1. Find user
    statement = select(Employee).where(Employee.email == form_data.username)
    employee = session.exec(statement).first()
    
    # 2. Check password
    if not employee or not verify_password(form_data.password, employee.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Generate Token, including role and ID in the payload
    access_token = create_access_token(
        data={"sub": employee.email, "role": employee.role, "id": employee.id},
        expires_delta=timedelta(minutes=500)
    )
    return {"access_token": access_token, "token_type": "bearer"}
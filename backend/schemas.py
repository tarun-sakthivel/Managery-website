# from typing import Optional, List
# from pydantic import BaseModel

# # --- Shared Properties ---
# class EmployeeBase(BaseModel):
#     name: str
#     email: str
#     department: str
#     role: str

# class TaskBase(BaseModel):
#     title: str
#     description: str
#     status: str
#     priority: str
#     due_date: str
#     employee_id: Optional[int] = None

# # --- API Request Schemas (Input) ---
# class EmployeeCreate(EmployeeBase):
#     from pydantic import Field
#     password: str = Field(min_length=8, max_length=64)  # Raw password input

# class EmployeeUpdate(BaseModel):
#     name: Optional[str] = None
#     department: Optional[str] = None
#     role: Optional[str] = None

# class TaskCreate(TaskBase):
#     pass

# class TaskUpdate(BaseModel):
#     title: Optional[str] = None
#     status: Optional[str] = None

# # --- API Response Schemas (Output) ---
# class TaskRead(TaskBase):
#     id: int

# class EmployeeRead(EmployeeBase):
#     id: int
#     tasks: List[TaskRead] = []

# class Token(BaseModel):
#     access_token: str
#     token_type: str

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlmodel import SQLModel
from models import RequestStatus
from datetime import datetime
# --- Employee Schemas ---

class EmployeeBase(SQLModel):
    name: str
    email: EmailStr
    department: str
    role: Optional[str] = "employee" # Can be set during creation

class EmployeeCreate(EmployeeBase):
    password: str # Password required only on creation

class EmployeeRead(EmployeeBase):
    id: int
    # Omit hashed_password for read operations

class EmployeeUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None


# --- Task Schemas ---

class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"
    owner_id: int

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: int

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    owner_id: Optional[int] = None

# --- Auth Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str
class ChangeRequestCreate(BaseModel):
    # What field the employee wants to change
    field_name: str
    # The new value they propose
    new_value: str

class ChangeRequestRead(SQLModel):
    id: int
    employee_id: int
    field_name: str
    new_value: str
    status: RequestStatus
    requested_at: datetime
    # Include other fields like processed_by_id if needed in the response

class ChangeRequestAction(BaseModel):
    # This schema is optional but good for explicit action definition
    action: str # Will be 'approve' or 'reject'
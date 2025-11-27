# from typing import Optional, List
# from sqlmodel import SQLModel, Field, Relationship

# # --- Database Tables ---

# class Employee(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str = Field(index=True)
#     email: str = Field(unique=True, index=True)
#     department: str
#     role: str
#     hashed_password: str  # New field for Auth
    
#     tasks: List["Task"] = Relationship(back_populates="employee")

# class Task(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     title: str
#     description: str
#     status: str = "Pending"
#     due_date: str
    
#     employee_id: Optional[int] = Field(default=None, foreign_key="employee.id")
#     employee: Optional[Employee] = Relationship(back_populates="tasks")
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum
from datetime import datetime, timezone

# --- Employee Model ---
class Employee(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    hashed_password: str
    department: str
    
    # NEW FIELD: Role for RBAC. Default to the least privileged role.
    role: str = Field(default="employee", index=True)
    
    # Relationships
    tasks: List["Task"] = Relationship(back_populates="owner")

# --- Task Model ---
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    priority: str = Field(default="medium") # high, medium, low
    status: str = Field(default="pending") # pending, in-progress, completed
    
    # Foreign Key to Employee
    owner_id: int = Field(index=True, foreign_key="employee.id")
    
    # Relationship to Employee
    owner: Employee = Relationship(back_populates="tasks")

class RequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class EmployeeChangeRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Link to the employee requesting the change
    employee_id: int = Field(foreign_key="employee.id", index=True)
    
    # What field is being changed (e.g., "email", "department")
    field_name: str
    
    # The value the employee wants to set
    new_value: str
    
    # Status of the request
    status: RequestStatus = Field(default=RequestStatus.PENDING)
    
    # Timestamps for tracking
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_by_id: Optional[int] = Field(default=None, foreign_key="employee.id")
    processed_at: Optional[datetime] = None
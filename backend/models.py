# # from pydantic import BaseModel, Field, EmailStr
# # from bson import ObjectId
# # from typing import Optional, List, Any
# # from datetime import datetime, timezone
# # from enum import Enum

# # # --- Custom ObjectId Type for Pydantic/MongoDB Interoperability ---
# # class PyObjectId(ObjectId):
# #     """
# #     Custom type for Pydantic to handle MongoDB's ObjectId.
# #     Enables validation and correct serialization.
# #     """
# #     @classmethod
# #     def __get_validators__(cls):
# #         yield cls.validate

# #     @classmethod
# #     def validate(cls, v):
# #         if not ObjectId.is_valid(v):
# #             raise ValueError("Invalid objectid")
# #         return ObjectId(v)

# #     def __repr__(self):
# #         return f"ObjectId('{self}')"

# # # --- Enums for Type Safety ---
# # class RequestStatus(str, Enum):
# #     PENDING = "pending"
# #     APPROVED = "approved"
# #     REJECTED = "rejected"

# # class Priority(str, Enum):
# #     LOW = "low"
# #     MEDIUM = "medium"
# #     HIGH = "high"

# # class TaskStatus(str, Enum):
# #     PENDING = "pending"
# #     IN_PROGRESS = "in_progress"
# #     COMPLETED = "completed"

# # # --- Base Configuration Class ---
# # class MongoModelConfig:
# #     """Configuration class for Pydantic models interacting with MongoDB."""
# #     allow_population_by_field_name = True
# #     arbitrary_types_allowed = True
# #     json_encoders = {ObjectId: str} # Ensure ObjectId is converted to string for JSON output


# # # --- Employee Models ---
# # class EmployeeInDB(BaseModel):
# #     """Internal model representing an employee document in the database."""
# #     id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
# #     name: str
# #     email: EmailStr
# #     hashed_password: str
# #     department: str
# #     role: str = Field(default="employee")
# #     created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# #     class Config(MongoModelConfig):
# #         pass

# # class EmployeeCreate(BaseModel):
# #     """Schema for creating a new employee."""
# #     name: str
# #     email: EmailStr
# #     password: str
# #     department: str
# #     role: str = "employee"

# # class EmployeeRead(BaseModel):
# #     """Schema for reading employee data (API response, excludes password hash)."""
# #     id: str = Field(alias="_id")
# #     name: str
# #     email: str
# #     department: str
# #     role: str

# #     class Config(MongoModelConfig):
# #         pass

# # # --- Task Models ---
# # class TaskInDB(BaseModel):
# #     """Internal model for a task document in the database."""
# #     id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
# #     title: str
# #     description: str
# #     priority: Priority = Field(default=Priority.MEDIUM) # Using Enum
# #     status: TaskStatus = Field(default=TaskStatus.PENDING) # Using Enum
# #     owner_id: str  # Reference to Employee's _id (string representation)
# #     owner_name: Optional[str] = None
# #     created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
# #     updated_at: Optional[datetime] = None

# #     class Config(MongoModelConfig):
# #         pass

# # class TaskCreate(BaseModel):
# #     """Schema for creating a new task."""
# #     title: str
# #     description: str
# #     priority: Priority = Field(default=Priority.MEDIUM)
# #     # Status is typically set by the API logic, but we allow an override if needed
# #     status: TaskStatus = Field(default=TaskStatus.PENDING) 

# # class TaskUpdate(BaseModel):
# #     """Schema for updating an existing task (all fields optional)."""
# #     title: Optional[str] = None
# #     description: Optional[str] = None
# #     priority: Optional[Priority] = None
# #     status: Optional[TaskStatus] = None
# #     owner_id: Optional[str] = None
# #     owner_name: Optional[str] = None

# # class TaskRead(BaseModel):
# #     """Schema for reading task data (API response)."""
# #     id: str = Field(alias="_id")
# #     title: str
# #     description: str
# #     priority: Priority
# #     status: TaskStatus
# #     owner_id: str
# #     owner_name: Optional[str]
# #     created_at: datetime
# #     updated_at: Optional[datetime] # Added updated_at to the Read model

# #     class Config(MongoModelConfig):
# #         pass


# # # --- Change Request Models ---
# # class ChangeRequestInDB(BaseModel):
# #     """Internal model for a change request document in the database."""
# #     id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
# #     employee_id: str  # Reference to Employee's _id
# #     field_name: str
# #     new_value: str
# #     status: RequestStatus = Field(default=RequestStatus.PENDING) # Using Enum
# #     requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
# #     processed_by_id: Optional[str] = None
# #     processed_at: Optional[datetime] = None

# #     class Config(MongoModelConfig):
# #         pass

# # class ChangeRequestCreate(BaseModel):
# #     """Schema for creating a new change request."""
# #     field_name: str
# #     new_value: str

# # class ChangeRequestUpdate(BaseModel):
# #     """Schema for updating a change request (typically for processing/approval)."""
# #     status: Optional[RequestStatus] = None # Only status can be updated via API endpoint
# #     processed_by_id: Optional[str] = None
# #     processed_at: Optional[datetime] = None

# # class ChangeRequestRead(BaseModel):
# #     """Schema for reading change request data (API response)."""
# #     id: str = Field(alias="_id")
# #     employee_id: str
# #     field_name: str
# #     new_value: str
# #     status: RequestStatus
# #     requested_at: datetime
# #     processed_by_id: Optional[str]
# #     processed_at: Optional[datetime]

# #     class Config(MongoModelConfig):
# #         pass

# # # --- API Response ---
# # class TokenResponse(BaseModel):
# #     """Schema for JWT token response."""
# #     access_token: str
# #     token_type: str = "bearer"
# from pydantic import BaseModel, Field, EmailStr
# from bson import ObjectId
# from typing import Optional, List, Any, Annotated
# from datetime import datetime, timezone
# from enum import Enum
# from pydantic_core import core_schema 

# # --- Custom ObjectId Type for Pydantic/MongoDB Interoperability ---
# class PyObjectId(ObjectId):
#     """
#     Custom type for Pydantic to handle MongoDB's ObjectId.
#     Uses the simplest V2 schema implementation to avoid internal function errors.
#     """
    
#     # 1. Validation Logic
#     @classmethod
#     def validate(cls, v):
#         """Converts the input (string or ObjectId) into a bson.ObjectId instance."""
#         if isinstance(v, (str, ObjectId)):
#             if not ObjectId.is_valid(str(v)):
#                 raise ValueError("Invalid objectid string")
#             return ObjectId(str(v))
#         raise TypeError(f"ObjectId must be a valid string or ObjectId, got {type(v)}")

#     # 2. Pydantic V2 Core Schema (Handles input validation)
#     @classmethod
#     def __get_pydantic_core_schema__(cls, source: Any, handler: Any) -> core_schema.CoreSchema:
#         """Defines how Pydantic validates PyObjectId inputs."""
#         return core_schema.json_or_python_schema(
#             # Python Schema: For Python objects (like ObjectId instances) passed in code
#             python_schema=core_schema.no_info_plain_validator_function(cls.validate),
            
#             # JSON Schema: For string IDs received from JSON input (e.g., in a POST body)
#             json_schema=core_schema.no_info_plain_validator_function(cls.validate),
#         )

#     # 3. Pydantic V2 JSON Schema (Ensures OpenAPI/Swagger documentation works)
#     @classmethod
#     def __get_pydantic_json_schema__(cls, core_schema: core_schema.CoreSchema, handler: Any) -> core_schema.JsonSchema:
#         # Represents this custom type as a standard string ID in FastAPI docs
#         return handler(core_schema.str_schema())
    
#     def __repr__(self):
#         return f"ObjectId('{self}')"

# # --- Enums for Type Safety ---
# class RequestStatus(str, Enum):
#     PENDING = "pending"
#     APPROVED = "approved"
#     REJECTED = "rejected"

# class Priority(str, Enum):
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"

# class TaskStatus(str, Enum):
#     PENDING = "pending"
#     IN_PROGRESS = "in_progress"
#     COMPLETED = "completed"

# # --- Base Configuration Class (Pydantic V2 adjustment) ---
# class MongoModelConfig:
#     """Configuration class for Pydantic models interacting with MongoDB."""
#     # V2 equivalent of allow_population_by_field_name = True
#     populate_by_name = True 
#     arbitrary_types_allowed = True
#     # CRITICAL: This handles the output serialization: whenever Pydantic sees an ObjectId, 
#     # it converts it to a standard Python string before JSON encoding.
#     json_encoders = {ObjectId: str} 

# # --- Employee Models ---
# class EmployeeInDB(BaseModel):
#     """Internal model representing an employee document in the database (includes hash)."""
#     # Use PyObjectId for the internal database ID
#     id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")] 
#     name: str
#     email: EmailStr
#     hashed_password: str
#     department: str
#     role: str = Field(default="employee")
#     created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

#     class Config(MongoModelConfig):
#         pass

# class UserInDB(EmployeeInDB):
#     """Alias for EmployeeInDB used specifically by the authentication dependency."""
#     pass 

# class EmployeeCreate(BaseModel):
#     """Schema for creating a new employee (API request body)."""
#     name: str
#     email: EmailStr
#     password: str # Plaintext password
#     department: str
#     role: str = "employee"

# class CreateUserRequest(EmployeeCreate):
#     """Alias for EmployeeCreate, used in auth.py for clarity/consistency."""
#     pass

# class EmployeeRead(BaseModel):
#     """Schema for reading employee data (API response, excludes password hash)."""
#     # Use str for API response IDs (when fetching from DB)
#     id: str = Field(alias="_id") 
#     name: str
#     email: str
#     department: str
#     role: str

#     class Config(MongoModelConfig):
#         pass

# # --- Task Models ---
# class TaskInDB(BaseModel):
#     """Internal model for a task document in the database."""
#     id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
#     title: str
#     description: str
#     priority: Priority = Field(default=Priority.MEDIUM) 
#     status: TaskStatus = Field(default=TaskStatus.PENDING) 
#     owner_id: str  # Reference to Employee's _id (string representation)
#     owner_name: Optional[str] = None
#     created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
#     updated_at: Optional[datetime] = None

#     class Config(MongoModelConfig):
#         pass

# class TaskCreate(BaseModel):
#     """Schema for creating a new task."""
#     title: str
#     description: str
#     priority: Priority = Field(default=Priority.MEDIUM)
#     status: TaskStatus = Field(default=TaskStatus.PENDING) 

# class TaskUpdate(BaseModel):
#     """Schema for updating an existing task (all fields optional for PATCH)."""
#     title: Optional[str] = None
#     description: Optional[str] = None
#     priority: Optional[Priority] = None
#     status: Optional[TaskStatus] = None
#     owner_id: Optional[str] = None
#     owner_name: Optional[str] = None

# class TaskRead(BaseModel):
#     """Schema for reading task data (API response)."""
#     id: str = Field(alias="_id")
#     title: str
#     description: str
#     priority: Priority
#     status: TaskStatus
#     owner_id: str
#     owner_name: Optional[str]
#     created_at: datetime
#     updated_at: Optional[datetime] 

#     class Config(MongoModelConfig):
#         pass


# # --- Change Request Models ---
# class ChangeRequestInDB(BaseModel):
#     """Internal model for a change request document in the database."""
#     id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias="_id")]
#     employee_id: str  # Reference to Employee's _id
#     field_name: str
#     new_value: str
#     status: RequestStatus = Field(default=RequestStatus.PENDING) 
#     requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
#     processed_by_id: Optional[str] = None
#     processed_at: Optional[datetime] = None

#     class Config(MongoModelConfig):
#         pass

# class ChangeRequestCreate(BaseModel):
#     """Schema for creating a new change request."""
#     field_name: str
#     new_value: str

# class ChangeRequestUpdate(BaseModel):
#     """Schema for updating a change request (e.g., changing status from pending to approved)."""
#     status: Optional[RequestStatus] = None 
#     processed_by_id: Optional[str] = None
#     processed_at: Optional[datetime] = None

# class ChangeRequestRead(BaseModel):
#     """Schema for reading change request data (API response)."""
#     id: str = Field(alias="_id")
#     employee_id: str
#     field_name: str
#     new_value: str
#     status: RequestStatus
#     requested_at: datetime
#     processed_by_id: Optional[str]
#     processed_at: Optional[datetime]

#     class Config(MongoModelConfig):
#         pass

# # --- API Response ---
# class TokenResponse(BaseModel):
#     """Schema for JWT token response."""
#     access_token: str
#     token_type: str = "bearer"
from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from bson import ObjectId
from typing import Optional, Annotated
from datetime import datetime, timezone
from enum import Enum
from typing_extensions import Self
from pydantic_core import core_schema as pc_core_schema # Renamed import to avoid variable shadowing

# --- Custom ObjectId Type for Pydantic/MongoDB Interoperability ---

# 1. Define a class to represent ObjectId behavior
class PyObjectId(ObjectId):
    """
    Custom type for Pydantic to handle MongoDB's ObjectId.
    It ensures Pydantic can validate and serialize ObjectId correctly.
    """
    @classmethod
    def __get_validators__(cls):
        # This V1 method is still often used for compatibility
        yield cls.validate 

    @classmethod
    def validate(cls, v, handler=None):
        """
        Custom validation logic for PyObjectId.
        Ensures the input is a valid ObjectId (or can be converted).
        """
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        # Check if running under Pydantic V2 context (where handler is passed)
        if handler is not None:
            raise ValueError("Invalid ObjectId format")
        # For V1 compatibility paths
        raise ValueError("Invalid ObjectId format")

    @classmethod
    def __get_pydantic_json_schema__(cls, input_schema: pc_core_schema.CoreSchema, handler) -> dict:
        """
        Pydantic V2 schema generation for OpenAPI/Swagger documentation.
        """
        # 1. Use the renamed imported module to get the string schema definition
        string_schema = pc_core_schema.str_schema() 
        
        # 2. Use the provided handler function to convert that core schema to a JSON dict
        json_schema = handler(string_schema)
        
        # 3. Add custom format details
        json_schema.update(type='string', format='objectid')
        return json_schema

    def __repr__(self):
        return f"ObjectId('{self}')"

# Type alias for MongoDB ObjectId fields in models
AnnotatedPyObjectId = Annotated[
    PyObjectId, 
    BeforeValidator(PyObjectId.validate)
]

# --- Enums for Type Safety ---
class RequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# --- Base Configuration DICTIONARY (V2 Syntax) ---
# This is a dictionary, compatible with Pydantic V2's model_config
MongoModelConfig = {
    # Ensure properties that map to field aliases (like id -> _id) are validated
    'populate_by_name': True,
    # Allow mapping MongoDB's ObjectId to a Pydantic str/PyObjectId
    'arbitrary_types_allowed': True,
    # Define custom JSON encoder for non-Pydantic types (like ObjectId and datetime)
    'json_encoders': {
        ObjectId: str,
        datetime: lambda dt: dt.isoformat(),
    },
    # Exclude extra fields from input validation
    'extra': "ignore" 
}

# --- Employee Models ---

class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    department: str
    role: str = Field(default="employee", pattern="^(employee|team_leader)$")
    
    model_config = MongoModelConfig

class EmployeeInDB(EmployeeBase):
    """Model used internally, including sensitive or internal fields."""
    id: AnnotatedPyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = MongoModelConfig

class EmployeeCreate(EmployeeBase):
    password: str = Field(min_length=8, max_length=64)
    # Uses model_config from EmployeeBase

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    role: Optional[str] = None # Should only be updated by a Team Leader
    
    model_config = MongoModelConfig

class EmployeeRead(EmployeeBase):
    """Model used for API responses (excludes password hash)."""
    # Use str for ID in API response
    id: str = Field(alias="_id")

    model_config = MongoModelConfig

# --- Task Models ---

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Field(default=Priority.MEDIUM)
    status: TaskStatus = Field(default=TaskStatus.PENDING)

    model_config = MongoModelConfig

class TaskCreate(TaskBase):
    owner_id: str = Field(description="Employee ID (ObjectId) of the task owner.")
    # Uses model_config from TaskBase

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[TaskStatus] = None
    owner_id: Optional[str] = None

    model_config = MongoModelConfig

class TaskInDB(TaskBase):
    id: AnnotatedPyObjectId = Field(default_factory=PyObjectId, alias="_id")
    owner_id: str
    owner_name: Optional[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    model_config = MongoModelConfig


# Change Request Models
class ChangeRequestInDB(BaseModel):
    id: AnnotatedPyObjectId = Field(default_factory=PyObjectId, alias="_id")
    employee_id: str
    field_name: str
    new_value: str
    status: RequestStatus = Field(default=RequestStatus.PENDING)
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_by_id: Optional[str] = None
    processed_at: Optional[datetime] = None

    model_config = MongoModelConfig

class ChangeRequestCreate(BaseModel):
    field_name: str
    new_value: str
    
    model_config = MongoModelConfig

class ChangeRequestUpdate(BaseModel):
    status: Optional[RequestStatus] = None
    processed_by_id: Optional[str] = None
    processed_at: Optional[datetime] = None

    model_config = MongoModelConfig

class ChangeRequestRead(BaseModel):
    id: str = Field(alias="_id")
    employee_id: str
    field_name: str
    new_value: str
    status: RequestStatus
    requested_at: datetime
    processed_by_id: Optional[str] = None
    processed_at: Optional[datetime] = None
    
    model_config = MongoModelConfig
# import os
# from fastapi import APIRouter, Depends, HTTPException, status
# from typing import Annotated, Optional
# from pydantic import BaseModel, EmailStr, Field
# from starlette import status
# from passlib.context import CryptContext 
# from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
# from jose import jwt, JWTError
# from datetime import datetime, timedelta, timezone
# from dotenv import load_dotenv
# from motor.motor_asyncio import AsyncIOMotorCollection
# from bson import ObjectId # Required for PyObjectId usage, though handled in models.py

# # IMPORTANT: Load environment variables here just in case, though main.py should handle it.
# load_dotenv()

# # --- IMPORT MODELS & DEPENDENCY ---
# # We assume UserInDB, CreateUserRequest exist in models.py for auth
# from models import PyObjectId, EmployeeCreate, ChangeRequestCreate,EmployeeInDB
# from database import user_collection_dependency # Use the dependency defined in database.py

# # --- NEW MODELS (Assuming these are needed for Login/Register responses) ---
# # We need to define or re-import any missing models like EmployeeRead and TokenResponse
# # Since they weren't provided, I'll create mock definitions for Employee models
# class EmployeeCreate(BaseModel):
#     name: str
#     email: EmailStr
#     password: str
#     department: str
#     role: str = "employee"

# class EmployeeRead(BaseModel):
#     id: PyObjectId = Field(alias="_id")
#     name: str
#     email: EmailStr
#     department: str
#     role: str

#     class Config:
#         populate_by_name = True
#         json_encoders = {ObjectId: str}

# class TokenResponse(BaseModel):
#     access_token: str
#     token_type: str

# MAX_PASSWORD_BYTES = 72

# router = APIRouter(
#     prefix="/auth",
#     tags=["auth"],
# )

# bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2_Bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")
# secret_key = os.getenv("SECRET_KEY")
# algorithm = os.getenv("ALGORITHM")

# if not secret_key or not algorithm:
#     raise RuntimeError("SECRET_KEY and ALGORITHM must be set in environment variables.")

# # Updated models imported from models.py
# class Token(BaseModel):
#     access_token: str
#     token_type: str

# # Dependency for the Users/Employees collection
# collection_dependency = Annotated[AsyncIOMotorCollection, Depends(user_collection_dependency)]

# def get_password_hash(password):
#     return bcrypt_context.hash(password)

# def verify_password(plain_password, hashed_password):
#     return bcrypt_context.verify(plain_password, hashed_password)

# async def authenticate_user(username: str, password: str, collection: collection_dependency):
#     # Find user by email
#     user_doc = await collection.find_one({"email": username})

#     if not user_doc:
#         return None # Return None if not found, let the endpoint handle HTTPException

#     # Convert the MongoDB document to our Pydantic model
#     user = EmployeeInDB(**user_doc)

#     if not verify_password(password, user.hashed_password):
#         return None # Return None if password fails
        
#     return user

# # Refactored to accept dict data for flexible token creation (used in /login)
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = timedelta(minutes=260)):
#     encode = data.copy()
#     expires = datetime.now(timezone.utc) + expires_delta
#     encode.update({"exp": expires}) 
#     return jwt.encode(encode, secret_key, algorithm=algorithm)

# def get_current_user(token: str = Depends(OAuth2_Bearer)):
#     try:
#         payload = jwt.decode(token, secret_key, algorithms=[algorithm])
#         email: str = payload.get("email") # Changed from "sub" to "email" for clarity based on data below
#         user_id: str = payload.get("id")
#         user_role: str = payload.get("role")

#         if email is None or user_id is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
#         return {"email": email, "user_id": user_id, "role": user_role}
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

# # ----------------------------------------------------
# # ENDPOINT UPDATES (All new endpoints MUST be async)
# # ----------------------------------------------------

# @router.post("/", status_code=status.HTTP_201_CREATED)
# async def create_user(create_user_request: ChangeRequestCreate, collection: collection_dependency):
#     # Standard user creation endpoint (using UserInDB model structure)
#     existing_user_doc = await collection.find_one({"email": create_user_request.email})
#     if existing_user_doc:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists.")

#     hashed_password = get_password_hash(create_user_request.password)
    
#     new_user_data = {
#         "username": create_user_request.username,
#         "email": create_user_request.email,
#         "hashed_password": hashed_password,
#     }

#     result = await collection.insert_one(new_user_data)
#     return {"id": str(result.inserted_id), "message": "User created successfully"}

# @router.get("/")
# async def get_users(collection: collection_dependency):
#     # Retrieve all documents
#     user_docs = await collection.find().to_list(length=None)
#     users = [EmployeeInDB(**doc) for doc in user_docs]
#     return users

# @router.post("/token", response_model=TokenResponse) # Used for OAuth2PasswordRequestForm
# async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], collection: collection_dependency):
#     user = await authenticate_user(form_data.username, form_data.password, collection) 
    
#     if not user:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

#     # Use the refactored create_access_token
#     access_token = create_access_token(
#         data={"sub": user.email, "email": user.email, "id": str(user.id)}, 
#         expires_delta=timedelta(minutes=260)
#     )
    
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/login", response_model=TokenResponse)
# async def login(email: str, password: str, collection: collection_dependency):
#     # This endpoint is similar to /token but takes raw email/password fields
#     employee_doc = await collection.find_one({"email": email})
    
#     if not employee_doc:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
#     employee = EmployeeInDB(**employee_doc)
    
#     if not verify_password(password, employee.hashed_password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
#     # Generate token using employee data
#     access_token = create_access_token(
#         data={
#             "sub": employee.email,
#             "id": str(employee.id),
#             # Assuming 'role' is stored in the user document, default to 'employee'
#             "role": employee_doc.get("role", "employee"), 
#             "email": employee.email
#         }
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.post("/register", response_model=EmployeeRead)
# async def register(employee_data: EmployeeCreate, collection: collection_dependency):
#     # Check if user already exists
#     existing = await collection.find_one({"email": employee_data.email})
#     if existing:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
#     hashed_pwd = get_password_hash(employee_data.password)
    
#     # Prepare data for insertion (Pydantic model to dict)
#     emp_dict = employee_data.model_dump(exclude={"password"})
#     emp_dict["hashed_password"] = hashed_pwd
#     emp_dict["created_at"] = datetime.now(timezone.utc)
    
#     # Insert the new document
#     result = await collection.insert_one(emp_dict)
    
#     # Fetch the newly created document to ensure full fidelity for the response model
#     new_employee_doc = await collection.find_one({"_id": result.inserted_id})

#     if not new_employee_doc:
#          raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve registered user.")

#     # Return the data using the EmployeeRead model, mapping _id to id
#     return EmployeeRead(**new_employee_doc)

import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated, Optional
from datetime import timedelta, timezone, datetime

from motor.motor_asyncio import AsyncIOMotorCollection
from database import user_collection_dependency
from models import EmployeeCreate, EmployeeRead, EmployeeInDB
from security import get_password_hash, verify_password, create_access_token

from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["auth"])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# typed dependency
UserCollection = Annotated[AsyncIOMotorCollection, Depends(user_collection_dependency)]

async def authenticate_user(username: str, password: str, collection: AsyncIOMotorCollection) -> Optional[EmployeeInDB]:
    user_doc = await collection.find_one({"email": username})
    if not user_doc:
        return None
    user = EmployeeInDB(**user_doc)
    if not verify_password(password, user.hashed_password):
        return None
    return user

@router.post("/token", response_model=TokenResponse)
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], collection: UserCollection):
    user = await authenticate_user(form_data.username, form_data.password, collection)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(
        data={
            "id": str(user.id), 
            "email": user.email, 
            "name": user.name,
            "department": user.department,
            "role": user.role
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def register(employee_data: EmployeeCreate, collection: UserCollection):
    existing = await collection.find_one({"email": employee_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(employee_data.password)
    emp_dict = employee_data.model_dump(exclude={"password"})
    emp_dict["hashed_password"] = hashed
    emp_dict["created_at"] = datetime.now(timezone.utc)
    result = await collection.insert_one(emp_dict)
    new_doc = await collection.find_one({"_id": result.inserted_id})
    new_doc["_id"] = str(new_doc["_id"])
    return EmployeeRead(
    _id=str(new_doc["_id"]),
    name=new_doc["name"],
    email=new_doc["email"],
    department=new_doc["department"],
    role=new_doc["role"]
)



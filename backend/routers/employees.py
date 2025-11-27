# from fastapi import APIRouter, HTTPException, status
# from models import EmployeeRead, EmployeeCreate, ChangeRequestRead, ChangeRequestCreate
# from database import user_collection_dependency, changerequest_collection_dependency
# from security import get_password_hash
# from bson import ObjectId
# from typing import List
# from datetime import datetime, timezone

# router = APIRouter(prefix="/employees", tags=["Employees"])

# @router.post("/", response_model=EmployeeRead, status_code=201)
# def create_employee(employee: EmployeeCreate):
#     existing = user_collection_dependency.find_one({"email": employee.email})
#     if existing:
#         raise HTTPException(status_code=400, detail="Email already exists")
    
#     hashed_pwd = get_password_hash(employee.password)
    
#     emp_dict = employee.dict()
#     emp_dict["hashed_password"] = hashed_pwd
#     del emp_dict["password"]
#     emp_dict["created_at"] = datetime.now(timezone.utc)
    
#     result = user_collection_dependency.insert_one(emp_dict)
    
#     return EmployeeRead(
#         id=str(result.inserted_id),
#         name=employee.name,
#         email=employee.email,
#         department=employee.department,
#         role=employee.role
#     )

# @router.get("/", response_model=List[EmployeeRead])
# def list_employees(skip: int = 0, limit: int = 100):
#     employees = list(user_collection_dependency.find().skip(skip).limit(limit))
#     return [
#         EmployeeRead(
#             id=str(emp["_id"]),
#             name=emp["name"],
#             email=emp["email"],
#             department=emp["department"],
#             role=emp.get("role", "employee")
#         )
#         for emp in employees
#     ]

# @router.get("/{employee_id}", response_model=EmployeeRead)
# def get_employee(employee_id: str):
#     try:
#         employee = user_collection_dependency.find_one({"_id": ObjectId(employee_id)})
#     except:
#         raise HTTPException(status_code=400, detail="Invalid employee ID")
    
#     if not employee:
#         raise HTTPException(status_code=404, detail="Employee not found")
    
#     return EmployeeRead(
#         id=str(employee["_id"]),
#         name=employee["name"],
#         email=employee["email"],
#         department=employee["department"],
#         role=employee.get("role", "employee")
#     )

# @router.post("/{employee_id}/requests", response_model=ChangeRequestRead, status_code=201)
# def submit_change_request(employee_id: str, request: ChangeRequestCreate):
#     try:
#         emp_oid = ObjectId(employee_id)
#     except:
#         raise HTTPException(status_code=400, detail="Invalid employee ID")
    
#     employee = user_collection_dependency.find_one({"_id": emp_oid})
#     if not employee:
#         raise HTTPException(status_code=404, detail="Employee not found")
    
#     existing = changerequest_collection_dependency.find_one({
#         "employee_id": employee_id,
#         "field_name": request.field_name,
#         "status": "pending"
#     })
    
#     if existing:
#         raise HTTPException(status_code=400, detail=f"Pending request for {request.field_name} already exists")
    
#     change_req = {
#         "employee_id": employee_id,
#         "field_name": request.field_name,
#         "new_value": request.new_value,
#         "status": "pending",
#         "requested_at": datetime.now(timezone.utc),
#         "processed_by_id": None,
#         "processed_at": None
#     }
    
#     result = changerequest_collection_dependency.insert_one(change_req)
    
#     return ChangeRequestRead(
#         id=str(result.inserted_id),
#         employee_id=employee_id,
#         field_name=request.field_name,
#         new_value=request.new_value,
#         status="pending",
#         requested_at=change_req["requested_at"],
#         processed_by_id=None,
#         processed_at=None
#     )

# @router.get("/{employee_id}/requests", response_model=List[ChangeRequestRead])
# def get_employee_requests(employee_id: str):
#     try:
#         ObjectId(employee_id)
#     except:
#         raise HTTPException(status_code=400, detail="Invalid employee ID")
    
#     requests = list(changerequest_collection_dependency.find({"employee_id": employee_id}).sort("requested_at", -1))
    
#     return [
#         ChangeRequestRead(
#             id=str(req["_id"]),
#             employee_id=req["employee_id"],
#             field_name=req["field_name"],
#             new_value=req["new_value"],
#             status=req["status"],
#             requested_at=req["requested_at"],
#             processed_by_id=req.get("processed_by_id"),
#             processed_at=req.get("processed_at")
#         )
#         for req in requests
#     ]

from fastapi import APIRouter, HTTPException, Depends, status
from models import EmployeeRead, EmployeeCreate, ChangeRequestRead, ChangeRequestCreate
from database import user_collection_dependency, changerequest_collection_dependency
from security import get_password_hash
from bson import ObjectId
from typing import List
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorCollection

router = APIRouter(prefix="/employees", tags=["Employees"])

UserCollection = Depends(user_collection_dependency)
ChangeReqCollection = Depends(changerequest_collection_dependency)

@router.post("/", response_model=EmployeeRead, status_code=201)
async def create_employee(employee: EmployeeCreate, user_collection: AsyncIOMotorCollection = UserCollection):
    existing = await user_collection.find_one({"email": employee.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_pwd = get_password_hash(employee.password)
    emp_dict = employee.model_dump()
    emp_dict["hashed_password"] = hashed_pwd
    emp_dict.pop("password", None)
    emp_dict["created_at"] = datetime.now(timezone.utc)
    result = await user_collection.insert_one(emp_dict)
    new_doc = await user_collection.find_one({"_id": result.inserted_id})
    return EmployeeRead(**new_doc)

@router.get("/", response_model=List[EmployeeRead])
async def list_employees(skip: int = 0, limit: int = 100, user_collection: AsyncIOMotorCollection = UserCollection):
    cursor = user_collection.find().skip(skip).limit(limit)
    employees = await cursor.to_list(length=limit)
    for emp in employees:
        emp["_id"] = str(emp["_id"])
    return [EmployeeRead(**emp) for emp in employees]


@router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(employee_id: str, user_collection: AsyncIOMotorCollection = UserCollection):
    try:
        oid = ObjectId(employee_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid employee ID")
    doc = await user_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Employee not found")
    return EmployeeRead(**doc)

@router.post("/{employee_id}/requests", response_model=ChangeRequestRead, status_code=201)
async def submit_change_request(employee_id: str, request: ChangeRequestCreate,
                                user_collection: AsyncIOMotorCollection = UserCollection,
                                req_collection: AsyncIOMotorCollection = ChangeReqCollection):
    try:
        emp_oid = ObjectId(employee_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid employee ID")
    employee = await user_collection.find_one({"_id": emp_oid})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    existing = await req_collection.find_one({
        "employee_id": employee_id,
        "field_name": request.field_name,
        "status": "pending"
    })
    if existing:
        raise HTTPException(status_code=400, detail=f"Pending request for {request.field_name} already exists")
    change_req = {
        "employee_id": employee_id,
        "field_name": request.field_name,
        "new_value": request.new_value,
        "status": "pending",
        "requested_at": datetime.now(timezone.utc),
        "processed_by_id": None,
        "processed_at": None
    }
    result = await req_collection.insert_one(change_req)
    saved = await req_collection.find_one({"_id": result.inserted_id})
    return ChangeRequestRead(**saved)

@router.get("/{employee_id}/requests", response_model=List[ChangeRequestRead])
async def get_employee_requests(employee_id: str, req_collection: AsyncIOMotorCollection = ChangeReqCollection):
    try:
        ObjectId(employee_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid employee ID")
    cursor = req_collection.find({"employee_id": employee_id}).sort("requested_at", -1)
    reqs = await cursor.to_list(length=100)
    return [ChangeRequestRead(**r) for r in reqs]

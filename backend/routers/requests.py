# # from fastapi import APIRouter, Depends, HTTPException, status
# # from typing import List
# # from sqlmodel import Session, select
# # from models import EmployeeChangeRequest, Employee, RequestStatus
# # from schemas import ChangeRequestRead
# # from dependencies import require_team_leader, SessionDep
# # from datetime import datetime, timezone

# # router = APIRouter(prefix="/requests", tags=["Change Requests"])

# # # --- TL: Read All Pending Requests ---
# # @router.get("/", response_model=List[ChangeRequestRead])
# # def get_all_pending_requests(session: SessionDep, user_data: dict = Depends(require_team_leader)):
# #     """Team Leaders view all pending change requests."""
# #     return session.exec(
# #         select(EmployeeChangeRequest)
# #         .where(EmployeeChangeRequest.status == RequestStatus.PENDING)
# #         .order_by(EmployeeChangeRequest.requested_at.asc())
# #     ).all()

# # # --- TL: Approve/Reject Request ---
# # @router.put("/{request_id}/{action}", response_model=ChangeRequestRead)
# # def process_change_request(
# #     request_id: int, 
# #     action: str, # Must be 'approve' or 'reject'
# #     session: SessionDep, 
# #     team_leader_data: dict = Depends(require_team_leader) # Ensures only TL can access
# # ):
# #     """Approves or rejects an employee change request and applies changes if approved."""
    
# #     # 1. Input Validation
# #     if action not in ["approve", "reject"]:
# #         raise HTTPException(status_code=400, detail="Invalid action. Must be 'approve' or 'reject'.")

# #     # 2. Fetch and Validate Request
# #     db_request = session.get(EmployeeChangeRequest, request_id)
# #     if not db_request:
# #         raise HTTPException(status_code=404, detail="Request not found.")
# #     if db_request.status != RequestStatus.PENDING:
# #         raise HTTPException(status_code=400, detail=f"Request already processed ({db_request.status}).")

# #     # 3. Process Action
# #     if action == "approve":
# #         employee = session.get(Employee, db_request.employee_id)
# #         if not employee:
# #             raise HTTPException(status_code=404, detail="Target employee not found.")
            
# #         # A. Update Employee Detail (The core change)
# #         setattr(employee, db_request.field_name, db_request.new_value)
# #         session.add(employee)
        
# #         # B. Update Request Status
# #         db_request.status = RequestStatus.APPROVED
    
# #     else: # reject
# #         db_request.status = RequestStatus.REJECTED

# #     # 4. Finalize Request Record
# #     db_request.processed_by_id = team_leader_data.get("id") 
# #     db_request.processed_at = datetime.now(timezone.utc)
    
# #     session.add(db_request)
# #     session.commit()
# #     session.refresh(db_request)
# #     return db_request


# from fastapi import APIRouter, Depends, HTTPException, status
# from typing import List, Dict
# from models import ChangeRequestRead, RequestStatus
# from database import changerequest_collection_dependency, user_collection_dependency
# from security import require_team_leader
# from motor.motor_asyncio import AsyncIOMotorCollection
# from bson import ObjectId
# from datetime import datetime, timezone

# router = APIRouter(prefix="/requests", tags=["Change Requests"])

# # Dependency aliases for clarity
# ChangeRequestCollection = Depends(changerequest_collection_dependency)
# EmployeeCollection = Depends(user_collection_dependency)
# TeamLeaderData = Depends(require_team_leader)

# # --- GET /requests/ (Read All Pending Requests - Team Leader Only) ---
# @router.get("/", response_model=List[ChangeRequestRead])
# async def get_all_pending_requests(
#     change_requests_collection: AsyncIOMotorCollection = ChangeRequestCollection, 
#     user_data: Dict = TeamLeaderData # Ensures only TL can access
# ):
#     """Team Leaders view all pending change requests."""
#     # Find requests where status is "pending" and sort by requested_at ascending
#     requests_cursor = change_requests_collection.find({"status": RequestStatus.PENDING}).sort("requested_at", 1)
#     requests = await requests_cursor.to_list(length=None)
    
#     return [ChangeRequestRead(**req) for req in requests]

# # --- PUT /requests/{request_id}/{action} (Approve/Reject Request - Team Leader Only) ---
# @router.put("/{request_id}/{action}", response_model=ChangeRequestRead)
# async def process_change_request(
#     request_id: str, 
#     action: str, # Must be 'approve' or 'reject'
#     change_requests_collection: AsyncIOMotorCollection = ChangeRequestCollection,
#     employees_collection: AsyncIOMotorCollection = EmployeeCollection,
#     team_leader_data: Dict = TeamLeaderData # Ensures only TL can access
# ):
#     """Approves or rejects an employee change request and applies changes if approved."""
    
#     # 1. Input Validation and ID conversion
#     if action not in ["approve", "reject"]:
#         raise HTTPException(status_code=400, detail="Invalid action. Must be 'approve' or 'reject'.")

#     try:
#         request_oid = ObjectId(request_id)
#     except:
#         raise HTTPException(status_code=400, detail="Invalid request ID format")

#     # 2. Fetch and Validate Request
#     db_request = await change_requests_collection.find_one({"_id": request_oid})

#     if not db_request:
#         raise HTTPException(status_code=404, detail="Request not found.")
        
#     if db_request.get("status") != RequestStatus.PENDING:
#         raise HTTPException(status_code=400, detail=f"Request already processed ({db_request.get('status')}).")

#     # 3. Process Action
#     update_data = {
#         "status": RequestStatus.REJECTED if action == "reject" else RequestStatus.APPROVED,
#         "processed_by_id": team_leader_data.get("id"),
#         "processed_at": datetime.now(timezone.utc)
#     }
    
#     if action == "approve":
#         employee_id_str = db_request.get("employee_id")
#         field_name = db_request.get("field_name")
#         new_value = db_request.get("new_value")

#         try:
#             employee_oid = ObjectId(employee_id_str)
#         except:
#              raise HTTPException(status_code=500, detail="Internal Error: Invalid employee_id in request.")

#         # A. Update Employee Detail (The core change)
#         employee_update_result = await employees_collection.update_one(
#             {"_id": employee_oid},
#             {"$set": {field_name: new_value}}
#         )
        
#         if employee_update_result.matched_count == 0:
#             raise HTTPException(status_code=404, detail="Target employee not found or ID mismatch.")
    
#     # 4. Update the Request document
#     await change_requests_collection.update_one(
#         {"_id": request_oid},
#         {"$set": update_data}
#     )
    
#     # Fetch and return the updated request document
#     updated_request_doc = await change_requests_collection.find_one({"_id": request_oid})
#     return ChangeRequestRead(**updated_request_doc)

# from fastapi import APIRouter, Depends, HTTPException
# from typing import List, Dict
# from models import ChangeRequestRead, RequestStatus
# from database import changerequest_collection_dependency, user_collection_dependency
# from security import require_team_leader
# from motor.motor_asyncio import AsyncIOMotorCollection
# from bson import ObjectId
# from datetime import datetime, timezone

# router = APIRouter(prefix="/requests", tags=["Change Requests"])

# CRCollection = Depends(changerequest_collection_dependency)
# EmployeeCollection = Depends(user_collection_dependency)
# TL = Depends(require_team_leader)

# @router.get("/", response_model=List[ChangeRequestRead])
# async def get_all_pending_requests(change_requests_collection: AsyncIOMotorCollection = CRCollection, user_data: Dict = TL):
#     cursor = change_requests_collection.find({"status": RequestStatus.PENDING}).sort("requested_at", 1)
#     reqs = await cursor.to_list(length=None)
#     return [ChangeRequestRead(**r) for r in reqs]

# @router.put("/{request_id}/{action}", response_model=ChangeRequestRead)
# async def process_change_request(request_id: str, action: str,
#                                  change_requests_collection: AsyncIOMotorCollection = CRCollection,
#                                  employees_collection: AsyncIOMotorCollection = EmployeeCollection,
#                                  team_leader_data: Dict = TL):
#     if action not in ["approve", "reject"]:
#         raise HTTPException(status_code=400, detail="Invalid action")
#     try:
#         request_oid = ObjectId(request_id)
#     except:
#         raise HTTPException(status_code=400, detail="Invalid request ID")
#     db_request = await change_requests_collection.find_one({"_id": request_oid})
#     if not db_request:
#         raise HTTPException(status_code=404, detail="Request not found")
#     if db_request.get("status") != RequestStatus.PENDING:
#         raise HTTPException(status_code=400, detail="Request already processed")
#     update_data = {
#         "status": RequestStatus.REJECTED if action == "reject" else RequestStatus.APPROVED,
#         "processed_by_id": team_leader_data.get("id"),
#         "processed_at": datetime.now(timezone.utc)
#     }
#     if action == "approve":
#         employee_id_str = db_request.get("employee_id")
#         field_name = db_request.get("field_name")
#         new_value = db_request.get("new_value")
#         try:
#             employee_oid = ObjectId(employee_id_str)
#         except:
#             raise HTTPException(status_code=500, detail="Invalid employee_id in request")
#         res = await employees_collection.update_one({"_id": employee_oid}, {"$set": {field_name: new_value}})
#         if res.matched_count == 0:
#             raise HTTPException(status_code=404, detail="Target employee not found")
#     await change_requests_collection.update_one({"_id": request_oid}, {"$set": update_data})
#     updated = await change_requests_collection.find_one({"_id": request_oid})
#     return ChangeRequestRead(**updated)

# from fastapi import APIRouter, Depends, HTTPException, status, Query
# from typing import List, Dict, Optional
# from motor.motor_asyncio import AsyncIOMotorCollection
# from bson import ObjectId
# from datetime import datetime, timezone

# from database import changerequest_collection_dependency, user_collection_dependency
# from security import require_team_leader, get_current_user_data
# from models import ChangeRequestCreate, ChangeRequestRead, RequestStatus

# router = APIRouter(prefix="/requests", tags=["Change Requests"])

# # dependencies (typed aliases for clarity)
# CRCollection = Depends(changerequest_collection_dependency)
# EmployeeCollection = Depends(user_collection_dependency)
# CurrentUser = Depends(get_current_user_data)
# TeamLeader = Depends(require_team_leader)

# # allowed fields that employees may request to change
# ALLOWED_FIELDS = {"name", "email", "department", "role"}


# # -------------------------
# # Helpers
# # -------------------------
# def serialize_doc(doc: dict) -> dict:
#     """
#     Convert ObjectId fields (including _id) to strings so Pydantic models accept them.
#     This mutates the input dict in-place and returns it for convenience.
#     """
#     if not doc:
#         return doc
#     # _id
#     if "_id" in doc and isinstance(doc["_id"], ObjectId):
#         doc["_id"] = str(doc["_id"])
#     # other ObjectId values (employee_id, processed_by_id, etc.)
#     for k, v in list(doc.items()):
#         if isinstance(v, ObjectId):
#             doc[k] = str(v)
#     return doc


# # -------------------------
# # Employee: Submit a change request
# # -------------------------
# @router.post("/", response_model=ChangeRequestRead, status_code=status.HTTP_201_CREATED)
# async def submit_change_request(
#     payload: ChangeRequestCreate,
#     cr_collection: AsyncIOMotorCollection = CRCollection,
#     employees_collection: AsyncIOMotorCollection = EmployeeCollection,
#     user_data: Dict = CurrentUser,
# ):
#     """
#     Employee submits a change request for one of the allowed fields.
#     The request is created with status='pending' and requested_at timestamp.
#     """
#     employee_id = user_data.get("id")
#     if not employee_id:
#         raise HTTPException(status_code=401, detail="Invalid user session")

#     # Validate field_name
#     if payload.field_name not in ALLOWED_FIELDS:
#         raise HTTPException(
#             status_code=400,
#             detail=f"field_name must be one of: {', '.join(sorted(ALLOWED_FIELDS))}"
#         )

#     # Ensure employee exists (defensive)
#     try:
#         emp_oid = ObjectId(employee_id)
#     except:
#         raise HTTPException(status_code=500, detail="Internal error: invalid employee id in token")

#     emp_doc = await employees_collection.find_one({"_id": emp_oid})
#     if not emp_doc:
#         raise HTTPException(status_code=404, detail="Employee not found")

#     # Prevent duplicate pending request for same field
#     existing = await cr_collection.find_one({
#         "employee_id": employee_id,
#         "field_name": payload.field_name,
#         "status": RequestStatus.PENDING
#     })
#     if existing:
#         raise HTTPException(
#             status_code=400,
#             detail=f"A pending request for '{payload.field_name}' already exists."
#         )

#     # If changing email, ensure new email is not already used (quick pre-check)
#     if payload.field_name == "email":
#         conflict = await employees_collection.find_one({"email": payload.new_value})
#         if conflict:
#             # If the conflict is the same employee (unlikely), allow; otherwise block
#             if str(conflict.get("_id")) != employee_id:
#                 raise HTTPException(status_code=400, detail="Email already in use by another account.")

#     # Insert the change request
#     change_doc = {
#         "employee_id": employee_id,
#         "field_name": payload.field_name,
#         "new_value": payload.new_value,
#         "status": RequestStatus.PENDING,
#         "requested_at": datetime.now(timezone.utc),
#         "processed_by_id": None,
#         "processed_at": None,
#     }

#     res = await cr_collection.insert_one(change_doc)
#     saved = await cr_collection.find_one({"_id": res.inserted_id})
#     serialize_doc(saved)
#     return ChangeRequestRead(**saved)


# # -------------------------
# # Employee: List my requests
# # -------------------------
# @router.get("/mine", response_model=List[ChangeRequestRead])
# async def list_my_requests(
#     cr_collection: AsyncIOMotorCollection = CRCollection,
#     user_data: Dict = CurrentUser,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=1000),
# ):
#     """
#     List change requests submitted by the current user (employee).
#     Supports basic pagination.
#     """
#     employee_id = user_data.get("id")
#     cursor = cr_collection.find({"employee_id": employee_id}).sort("requested_at", -1).skip(skip).limit(limit)
#     docs = await cursor.to_list(length=limit)
#     return [ChangeRequestRead(**serialize_doc(dict(doc))) for doc in docs]


# # -------------------------
# # Team Leader: Get pending/all requests (RBAC)
# # -------------------------
# @router.get("/", response_model=List[ChangeRequestRead], dependencies=[TeamLeader])
# async def get_requests_for_tl(
#     cr_collection: AsyncIOMotorCollection = CRCollection,
#     status: Optional[RequestStatus] = Query(None, description="Filter by status"),
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=1000),
# ):
#     """
#     Team leader endpoint to list change requests. Filter by status optional.
#     """
#     q = {}
#     if status:
#         q["status"] = status
#     cursor = cr_collection.find(q).sort("requested_at", -1).skip(skip).limit(limit)
#     docs = await cursor.to_list(length=limit)
#     return [ChangeRequestRead(**serialize_doc(dict(doc))) for doc in docs]


# # -------------------------
# # Team Leader: Approve or Reject a request
# # -------------------------
# @router.put("/{request_id}/{action}", response_model=ChangeRequestRead)
# async def process_change_request(
#     request_id: str,
#     action: str,  # 'approve' or 'reject'
#     cr_collection: AsyncIOMotorCollection = CRCollection,
#     employees_collection: AsyncIOMotorCollection = EmployeeCollection,
#     team_leader_data: Dict = TeamLeader,
# ):
#     """
#     Approve or reject a change request. Only Team Leaders can call this.
#     When approving, the employee document is updated atomically and the request is marked approved.
#     When rejecting, only the request status is updated.
#     """

#     action = action.lower()
#     if action not in ("approve", "reject"):
#         raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")

#     try:
#         req_oid = ObjectId(request_id)
#     except:
#         raise HTTPException(status_code=400, detail="Invalid request ID format")

#     db_request = await cr_collection.find_one({"_id": req_oid})

# routers/requests.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from datetime import datetime, timezone

from database import changerequest_collection_dependency, user_collection_dependency
from security import require_team_leader, get_current_user_data
from models import ChangeRequestCreate, ChangeRequestRead, RequestStatus

router = APIRouter(prefix="/requests", tags=["Change Requests"])

# dependencies (typed aliases for clarity)
CRCollection = Depends(changerequest_collection_dependency)
EmployeeCollection = Depends(user_collection_dependency)
CurrentUser = Depends(get_current_user_data)
TeamLeader = Depends(require_team_leader)

# allowed fields that employees may request to change
ALLOWED_FIELDS = {"name", "email", "department", "role"}


# -------------------------
# Helpers
# -------------------------
def serialize_doc(doc: dict) -> dict:
    """
    Convert ObjectId fields (including _id) to strings so Pydantic models accept them.
    This mutates the input dict in-place and returns it for convenience.
    """
    if not doc:
        return doc
    # _id
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    # other ObjectId values (employee_id, processed_by_id, etc.)
    for k, v in list(doc.items()):
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc


# -------------------------
# Employee: Submit a change request
# -------------------------
@router.post("/", response_model=ChangeRequestRead, status_code=status.HTTP_201_CREATED)
async def submit_change_request(
    payload: ChangeRequestCreate,
    cr_collection: AsyncIOMotorCollection = CRCollection,
    employees_collection: AsyncIOMotorCollection = EmployeeCollection,
    user_data: Dict = CurrentUser,
):
    """
    Employee submits a change request for one of the allowed fields.
    The request is created with status='pending' and requested_at timestamp.
    """
    employee_id = user_data.get("id")
    if not employee_id:
        raise HTTPException(status_code=401, detail="Invalid user session")

    # Validate field_name
    if payload.field_name not in ALLOWED_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"field_name must be one of: {', '.join(sorted(ALLOWED_FIELDS))}"
        )

    # Ensure employee exists (defensive)
    try:
        emp_oid = ObjectId(employee_id)
    except:
        raise HTTPException(status_code=500, detail="Internal error: invalid employee id in token")

    emp_doc = await employees_collection.find_one({"_id": emp_oid})
    if not emp_doc:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Prevent duplicate pending request for same field
    existing = await cr_collection.find_one({
        "employee_id": employee_id,
        "field_name": payload.field_name,
        "status": RequestStatus.PENDING
    })
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"A pending request for '{payload.field_name}' already exists."
        )

    # If changing email, ensure new email is not already used (quick pre-check)
    if payload.field_name == "email":
        conflict = await employees_collection.find_one({"email": payload.new_value})
        if conflict:
            # If the conflict is the same employee (unlikely), allow; otherwise block
            if str(conflict.get("_id")) != employee_id:
                raise HTTPException(status_code=400, detail="Email already in use by another account.")

    # Insert the change request
    change_doc = {
        "employee_id": employee_id,
        "field_name": payload.field_name,
        "new_value": payload.new_value,
        "status": RequestStatus.PENDING,
        "requested_at": datetime.now(timezone.utc),
        "processed_by_id": None,
        "processed_at": None,
    }

    res = await cr_collection.insert_one(change_doc)
    saved = await cr_collection.find_one({"_id": res.inserted_id})
    serialize_doc(saved)
    return ChangeRequestRead(**saved)


# -------------------------
# Employee: List my requests
# -------------------------
@router.get("/mine", response_model=List[ChangeRequestRead])
async def list_my_requests(
    cr_collection: AsyncIOMotorCollection = CRCollection,
    user_data: Dict = CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    List change requests submitted by the current user (employee).
    Supports basic pagination.
    """
    employee_id = user_data.get("id")
    cursor = cr_collection.find({"employee_id": employee_id}).sort("requested_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [ChangeRequestRead(**serialize_doc(dict(doc))) for doc in docs]


# -------------------------
# Team Leader: Get pending/all requests (RBAC)
# -------------------------
@router.get("/", response_model=List[ChangeRequestRead], dependencies=[TeamLeader])
async def get_requests_for_tl(
    cr_collection: AsyncIOMotorCollection = CRCollection,
    status: Optional[RequestStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Team leader endpoint to list change requests. Filter by status optional.
    """
    q = {}
    if status:
        q["status"] = status
    cursor = cr_collection.find(q).sort("requested_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [ChangeRequestRead(**serialize_doc(dict(doc))) for doc in docs]


# -------------------------
# Team Leader: Approve or Reject a request
# -------------------------
@router.put("/{request_id}/{action}", response_model=ChangeRequestRead)
async def process_change_request(
    request_id: str,
    action: str,  # 'approve' or 'reject'
    cr_collection: AsyncIOMotorCollection = CRCollection,
    employees_collection: AsyncIOMotorCollection = EmployeeCollection,
    team_leader_data: Dict = TeamLeader,
):
    """
    Approve or reject a change request. Only Team Leaders can call this.
    When approving, the employee document is updated atomically and the request is marked approved.
    When rejecting, only the request status is updated.
    """

    action = action.lower()
    if action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")

    try:
        req_oid = ObjectId(request_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid request ID format")

    db_request = await cr_collection.find_one({"_id": req_oid})
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Only allow processing pending requests
    if db_request.get("status") != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Request already processed ({db_request.get('status')}).")

    # Prepare update metadata
    update_data = {
        "status": RequestStatus.APPROVED if action == "approve" else RequestStatus.REJECTED,
        "processed_by_id": team_leader_data.get("id"),
        "processed_at": datetime.now(timezone.utc),
    }

    # If approving -> update employee field
    if action == "approve":
        employee_id_str = db_request.get("employee_id")
        field_name = db_request.get("field_name")
        new_value = db_request.get("new_value")

        # Validate allowed field
        if field_name not in ALLOWED_FIELDS:
            raise HTTPException(status_code=400, detail="Requested field is not allowed to change.")

        # convert employee id to ObjectId (defensive)
        try:
            employee_oid = ObjectId(employee_id_str)
        except:
            raise HTTPException(status_code=500, detail="Invalid employee_id stored in request")

        # If changing email, ensure no other user has this email
        if field_name == "email":
            conflict = await employees_collection.find_one({"email": new_value})
            if conflict and str(conflict.get("_id")) != employee_id_str:
                raise HTTPException(status_code=400, detail="Email already used by another account.")

        res = await employees_collection.update_one({"_id": employee_oid}, {"$set": {field_name: new_value}})
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Target employee not found")

    # Update the request document
    await cr_collection.update_one({"_id": req_oid}, {"$set": update_data})

    # Fetch the updated request and return it
    updated = await cr_collection.find_one({"_id": req_oid})
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to fetch updated request")

    serialize_doc(updated)
    return ChangeRequestRead(**updated)

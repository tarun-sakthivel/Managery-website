# # from fastapi import APIRouter, Depends, HTTPException, status
# # from typing import List, Optional
# # from sqlmodel import Session, select
# # from database import get_session
# # from models import Task, Employee
# # from schemas import TaskCreate, TaskRead, TaskUpdate
# # from dependencies import CurrentEmployee, require_team_leader, SessionDep, CurrentUserData
# # from bson import ObjectId
# # from datetime import datetime, timezone

# # router = APIRouter(prefix="/tasks", tags=["Tasks"])

# # # --- CREATE (Both Roles) ---
# # @router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
# # def create_task(task: TaskCreate, owner_id: str):
# #     try:
# #         owner_oid = ObjectId(owner_id)
# #     except:
# #         raise HTTPException(status_code=400, detail="Invalid owner ID")
    
# #     employee = employees_collection.find_one({"_id": owner_oid})
# #     if not employee:
# #         raise HTTPException(status_code=404, detail="Employee not found")
    
# #     task_dict = task.dict()
# #     task_dict["owner_id"] = owner_id
# #     task_dict["owner_name"] = employee["name"]
# #     task_dict["created_at"] = datetime.now(timezone.utc)
    
# #     result = tasks_collection.insert_one(task_dict)
    
# #     return TaskRead(
# #         id=str(result.inserted_id),
# #         title=task.title,
# #         description=task.description,
# #         priority=task.priority,
# #         status=task.status,
# #         owner_id=owner_id,
# #         owner_name=employee["name"],
# #         created_at=task_dict["created_at"]
# #     )

# # # --- READ ALL (Team Leader Only) ---
# # @router.get("/", response_model=List[TaskRead])
# # def read_all_tasks(session: SessionDep, user_data: dict = Depends(require_team_leader)):
# #     """Only Team Leaders can view all tasks."""
# #     return session.exec(select(Task)).all()

# # # --- READ SINGLE (Assigned Employee or Team Leader) ---
# # @router.get("/{task_id}", response_model=TaskRead)
# # def read_single_task(task_id: str):
# #     try:
# #         task = tasks_collection.find_one({"_id": ObjectId(task_id)})
# #     except:
# #         raise HTTPException(status_code=400, detail="Invalid task ID")
    
# #     if not task:
# #         raise HTTPException(status_code=404, detail="Task not found")
    
# #     return TaskRead(
# #         id=str(task["_id"]),
# #         title=task["title"],
# #         description=task["description"],
# #         priority=task["priority"],
# #         status=task["status"],
# #         owner_id=task["owner_id"],
# #         owner_name=task.get("owner_name"),
# #         created_at=task["created_at"]
# #     )


# from fastapi import APIRouter, Depends, HTTPException, status
# from typing import List, Dict, Optional
# from models import TaskCreate, TaskRead, TaskUpdate
# from database import task_collection_dependency, user_collection_dependency
# from security import get_current_user_data, require_team_leader
# from motor.motor_asyncio import AsyncIOMotorCollection
# from bson import ObjectId
# from datetime import datetime, timezone

# router = APIRouter(prefix="/tasks", tags=["Tasks"])

# # Dependency aliases for clarity
# TaskCollection = Depends(task_collection_dependency)
# EmployeeCollection = Depends(user_collection_dependency)
# CurrentUserData = Depends(get_current_user_data)
# TeamLeaderData = Depends(require_team_leader)

# # --- POST /tasks/ (Create Task - Team Leader Only) ---
# @router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
# async def create_task(
#     task: TaskCreate, 
#     owner_id: str, # Owner ID is now passed as a query parameter or body field if you prefer
#     tasks_collection: AsyncIOMotorCollection = TaskCollection,
#     employees_collection: AsyncIOMotorCollection = EmployeeCollection,
#     user_data: Dict = TeamLeaderData # Ensures only TL can create tasks
# ):
#     try:
#         owner_oid = ObjectId(owner_id)
#     except:
#         raise HTTPException(status_code=400, detail="Invalid owner ID format")
    
#     # Verify the assigned employee exists
#     employee = await employees_collection.find_one({"_id": owner_oid})
#     if not employee:
#         raise HTTPException(status_code=404, detail="Employee assigned as owner not found")
    
#     # Prepare the task document
#     task_dict = task.model_dump()
#     task_dict.update({
#         "owner_id": owner_id,
#         "owner_name": employee["name"],
#         "created_at": datetime.now(timezone.utc),
#         "updated_at": None # Initialize updated_at
#     })
    
#     result = await tasks_collection.insert_one(task_dict)
    
#     # Fetch inserted document to ensure correct Pydantic serialization
#     inserted_doc = await tasks_collection.find_one({"_id": result.inserted_id})
#     return TaskRead(**inserted_doc)


# # --- GET /tasks/ (Read All Tasks - Team Leader Only) ---
# @router.get("/", response_model=List[TaskRead])
# async def read_all_tasks(
#     tasks_collection: AsyncIOMotorCollection = TaskCollection,
#     user_data: Dict = TeamLeaderData # Requires Team Leader to view all tasks
# ):
#     """Only Team Leaders can view all tasks."""
#     tasks_cursor = tasks_collection.find().sort("created_at", -1)
#     tasks = await tasks_cursor.to_list(length=None)
    
#     return [TaskRead(**task) for task in tasks]


# # --- GET /tasks/mine (Read My Tasks - Assigned Employee Only) ---
# @router.get("/mine", response_model=List[TaskRead])
# async def read_my_tasks(
#     tasks_collection: AsyncIOMotorCollection = TaskCollection,
#     user_data: Dict = CurrentUserData
# ):
#     """Employees view only the tasks assigned to them."""
#     employee_id = user_data.get("id")
    
#     tasks_cursor = tasks_collection.find({"owner_id": employee_id}).sort("created_at", -1)
#     tasks = await tasks_cursor.to_list(length=None)
    
#     return [TaskRead(**task) for task in tasks]


# # --- GET /tasks/{task_id} (Read Single Task - Assigned Employee or TL) ---
# @router.get("/{task_id}", response_model=TaskRead)
# async def read_single_task(
#     task_id: str,
#     tasks_collection: AsyncIOMotorCollection = TaskCollection,
#     user_data: Dict = CurrentUserData
# ):
#     try:
#         task_oid = ObjectId(task_id)
#     except:
#         raise HTTPException(status_code=400, detail="Invalid task ID format")
    
#     task = await tasks_collection.find_one({"_id": task_oid})
    
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found")

#     # Access control: Must be the task owner or a Team Leader
#     if user_data.get("role") != "team_leader" and user_data.get("id") != task.get("owner_id"):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, 
#             detail="You are not authorized to view this task"
#         )
    
#     return TaskRead(**task)


# # --- PUT /tasks/{task_id} (Update Task - Assigned Employee or TL) ---
# @router.put("/{task_id}", response_model=TaskRead)
# async def update_task(
#     task_id: str,
#     task_update: TaskUpdate,
#     tasks_collection: AsyncIOMotorCollection = TaskCollection,
#     user_data: Dict = CurrentUserData
# ):
#     try:
#         task_oid = ObjectId(task_id)
#     except:
#         raise HTTPException(status_code=400, detail="Invalid task ID format")

#     # 1. Check if the task exists and get the original owner
#     original_task = await tasks_collection.find_one({"_id": task_oid})
#     if not original_task:
#         raise HTTPException(status_code=404, detail="Task not found")

#     # 2. Access control: Must be the task owner or a Team Leader
#     is_owner = user_data.get("id") == original_task.get("owner_id")
#     is_team_leader = user_data.get("role") == "team_leader"
    
#     if not (is_owner or is_team_leader):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, 
#             detail="You are not authorized to update this task"
#         )

#     # 3. Prepare the update data
#     update_data = task_update.model_dump(exclude_unset=True)
    
#     # Employee can only update status
#     if is_owner and not is_team_leader and any(k not in ["status"] for k in update_data.keys()):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, 
#             detail="Employees can only update the task status"
#         )
        
#     if not update_data:
#         return TaskRead(**original_task) # Nothing to update

#     update_data["updated_at"] = datetime.now(timezone.utc)
    
#     # 4. Perform the update
#     await tasks_collection.update_one(
#         {"_id": task_oid},
#         {"$set": update_data}
#     )

#     # 5. Fetch and return the updated document
#     updated_doc = await tasks_collection.find_one({"_id": task_oid})
#     return TaskRead(**updated_doc)


# # --- DELETE /tasks/{task_id} (Delete Task - Team Leader Only) ---
# @router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_task(
#     task_id: str,
#     tasks_collection: AsyncIOMotorCollection = TaskCollection,
#     user_data: Dict = TeamLeaderData # Requires Team Leader to delete tasks
# ):
#     try:
#         task_oid = ObjectId(task_id)
#     except:
#         raise HTTPException(status_code=400, detail="Invalid task ID format")
    
#     result = await tasks_collection.delete_one({"_id": task_oid})
    
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     return

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from models import TaskCreate, TaskRead, TaskUpdate
from database import task_collection_dependency, user_collection_dependency
from security import get_current_user_data, require_team_leader
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter(prefix="/tasks", tags=["Tasks"])

TaskCollection = Depends(task_collection_dependency)
EmployeeCollection = Depends(user_collection_dependency)
CurrentUser = Depends(get_current_user_data)
TL = Depends(require_team_leader)
def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, owner_id: str,
                      tasks_collection: AsyncIOMotorCollection = TaskCollection,
                      employees_collection: AsyncIOMotorCollection = EmployeeCollection,
                      user_data: dict = TL):
    try:
        owner_oid = ObjectId(owner_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid owner ID format")
    employee = await employees_collection.find_one({"_id": owner_oid})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee assigned as owner not found")
    task_dict = task.model_dump()
    task_dict.update({
        "owner_id": owner_id,
        "owner_name": employee["name"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": None
    })
    result = await tasks_collection.insert_one(task_dict)
    inserted_doc = await tasks_collection.find_one({"_id": result.inserted_id})
    return TaskRead(**serialize_doc(inserted_doc))


@router.get("/", response_model=List[TaskRead])
async def read_all_tasks(tasks_collection: AsyncIOMotorCollection = TaskCollection, user_data: dict = TL):
    cursor = tasks_collection.find().sort("created_at", -1)
    tasks = await cursor.to_list(length=None)
    return [TaskRead(**serialize_doc(t)) for t in tasks]


@router.get("/mine", response_model=List[TaskRead])
async def read_my_tasks(tasks_collection: AsyncIOMotorCollection = TaskCollection, user_data: dict = CurrentUser):
    employee_id = user_data.get("id")
    cursor = tasks_collection.find({"owner_id": employee_id}).sort("created_at", -1)
    tasks = await cursor.to_list(length=None)
    return [TaskRead(**t) for t in tasks]

@router.get("/{task_id}", response_model=TaskRead)
async def read_single_task(task_id: str, tasks_collection: AsyncIOMotorCollection = TaskCollection, user_data: dict = CurrentUser):
    try:
        task_oid = ObjectId(task_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    task = await tasks_collection.find_one({"_id": task_oid})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if user_data.get("role") != "team_leader" and user_data.get("id") != task.get("owner_id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to view this task")
    return TaskRead(**serialize_doc(task))


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(task_id: str, task_update: TaskUpdate, tasks_collection: AsyncIOMotorCollection = TaskCollection, user_data: dict = CurrentUser):
    try:
        task_oid = ObjectId(task_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    original_task = await tasks_collection.find_one({"_id": task_oid})
    if not original_task:
        raise HTTPException(status_code=404, detail="Task not found")
    is_owner = user_data.get("id") == original_task.get("owner_id")
    is_tl = user_data.get("role") == "team_leader"
    if not (is_owner or is_tl):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update")
    update_data = task_update.model_dump(exclude_unset=True)
    if is_owner and not is_tl and any(k not in ["status"] for k in update_data.keys()):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Employees can only update status")
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc)
        await tasks_collection.update_one({"_id": task_oid}, {"$set": update_data})
    updated = await tasks_collection.find_one({"_id": task_oid})
    return TaskRead(**serialize_doc(updated))




@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, tasks_collection: AsyncIOMotorCollection = TaskCollection, user_data: dict = TL):
    try:
        task_oid = ObjectId(task_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    result = await tasks_collection.delete_one({"_id": task_oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return

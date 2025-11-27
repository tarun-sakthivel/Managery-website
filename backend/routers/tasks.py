# from fastapi import APIRouter, Depends, HTTPException
# from typing import List
# from sqlmodel import Session, select
# from database import get_session
# from models import Task
# from schemas import TaskCreate, TaskRead, TaskUpdate
# from dependencies import get_current_employee

# router = APIRouter(prefix="/tasks", tags=["Tasks"])

# @router.post("/", response_model=TaskRead, status_code=201)
# def create_task(
#     task: TaskCreate, 
#     session: Session = Depends(get_session),
#     current_user = Depends(get_current_employee)
# ):
#     db_task = Task.model_validate(task)
#     session.add(db_task)
#     session.commit()
#     session.refresh(db_task)
#     return db_task

# @router.get("/", response_model=List[TaskRead])
# def read_tasks(session: Session = Depends(get_session), current_user = Depends(get_current_employee)):
#     return session.exec(select(Task)).all()

# @router.put("/{task_id}", response_model=TaskRead)
# def update_task(task_id: int, task_update: TaskUpdate, session: Session = Depends(get_session), current_user = Depends(get_current_employee)):
#     db_task = session.get(Task, task_id)
#     if not db_task:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     task_data = task_update.model_dump(exclude_unset=True)
#     for key, value in task_data.items():
#         setattr(db_task, key, value)
        
#     session.add(db_task)
#     session.commit()
#     session.refresh(db_task)
#     return db_task

# @router.delete("/{task_id}", status_code=204)
# def delete_task(task_id: int, session: Session = Depends(get_session), current_user = Depends(get_current_employee)):
#     db_task = session.get(Task, task_id)
#     if not db_task:
#         raise HTTPException(status_code=404, detail="Task not found")
#     session.delete(db_task)
#     session.commit()
#     return None

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlmodel import Session, select
from database import get_session
from models import Task, Employee
from schemas import TaskCreate, TaskRead, TaskUpdate
from dependencies import CurrentEmployee, require_team_leader, SessionDep, CurrentUserData

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# --- CREATE (Both Roles) ---
@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate, session: SessionDep, current_user: CurrentEmployee):
    """Allows both roles to create a task."""
    
    # Optional: You might want to restrict task creation to TL only, 
    # but based on the chat, both can create.
    
    # Check if the owner_id exists
    if not session.get(Employee, task_data.owner_id):
        raise HTTPException(status_code=400, detail="Assigned employee (owner_id) does not exist.")
    
    db_task = Task.model_validate(task_data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# --- READ ALL (Team Leader Only) ---
@router.get("/", response_model=List[TaskRead])
def read_all_tasks(session: SessionDep, user_data: dict = Depends(require_team_leader)):
    """Only Team Leaders can view all tasks."""
    return session.exec(select(Task)).all()

# --- READ SINGLE (Assigned Employee or Team Leader) ---
@router.get("/{task_id}", response_model=TaskRead)
def read_single_task(task_id: int, session: SessionDep, current_user: CurrentEmployee):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # Check if Team Leader OR the assigned owner
    if current_user.role == "team_leader" or task.owner_id == current_user.id:
        return task
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied to view this task.")

# --- UPDATE (Fine-Grained Logic) ---
@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task_update: TaskUpdate, session: SessionDep, current_user: CurrentEmployee):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    user_role = current_user.role
    
    # 1. Team Leader: Can update everything
    if user_role == "team_leader":
        update_data = task_update.model_dump(exclude_unset=True)
    
    # 2. Employee: Can only update status on their own task
    elif task.owner_id == current_user.id:
        update_data = {}
        if task_update.status is not None:
            update_data["status"] = task_update.status
        
        # Prevent employees from changing priority, owner, or title/description
        if any(field is not None for field in [task_update.priority, task_update.owner_id, task_update.title, task_update.description]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Employees can only update task status."
            )
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields provided for update.")
    
    # 3. Unauthorized
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied to update this task.")

    # Apply updates and commit
    task.sqlmodel_update(update_data)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# --- DELETE (Team Leader Only) ---
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, session: SessionDep, user_data: dict = Depends(require_team_leader)):
    """Only Team Leaders can delete tasks."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"ok": True}
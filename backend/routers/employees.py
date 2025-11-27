# from fastapi import APIRouter, Depends, HTTPException, status
# from typing import List
# from sqlmodel import Session, select
# from database import get_session
# from models import Employee
# from schemas import EmployeeCreate, EmployeeRead, EmployeeUpdate
# from security import get_password_hash
# from dependencies import get_current_employee

# router = APIRouter(prefix="/employees", tags=["Employees"])

# # Create (Registration - No Auth needed usually, or Admin only)
# @router.post("/", response_model=EmployeeRead, status_code=201)
# def create_employee(employee: EmployeeCreate, session: Session = Depends(get_session)):
#     hashed_pwd = get_password_hash(employee.password)
#     db_employee = Employee.model_validate(employee, update={"hashed_password": hashed_pwd})
#     session.add(db_employee)
#     session.commit()
#     session.refresh(db_employee)
#     return db_employee

# # Read All (Protected)
# @router.get("/", response_model=List[EmployeeRead])
# def read_employees(
#     skip: int = 0, 
#     limit: int = 100, 
#     session: Session = Depends(get_session),
#     current_user: Employee = Depends(get_current_employee) # Requires Token
# ):
#     return session.exec(select(Employee).offset(skip).limit(limit)).all()

# # Read One
# @router.get("/{employee_id}", response_model=EmployeeRead)
# def read_employee(employee_id: int, session: Session = Depends(get_session)):
#     employee = session.get(Employee, employee_id)
#     if not employee:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     return employee
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from database import get_session
from models import Employee
from schemas import EmployeeCreate, EmployeeRead, EmployeeUpdate
from security import get_password_hash
from dependencies import CurrentEmployee, require_team_leader, SessionDep
from models import Employee, EmployeeChangeRequest, RequestStatus
from schemas import EmployeeCreate, EmployeeRead, EmployeeUpdate, ChangeRequestCreate, ChangeRequestRead
from dependencies import CurrentEmployee, require_team_leader, SessionDep, CurrentUserData

router = APIRouter(prefix="/employees", tags=["Employees"])

# Create (Registration for new employees - RESTRICTED TO TEAM LEADER)
@router.post("/", response_model=EmployeeRead, status_code=201)
def create_employee(
    employee: EmployeeCreate, 
    session: SessionDep,
    # Requires Team Leader to create employees via this endpoint
    user_data: dict = Depends(require_team_leader) 
):
    # This endpoint is redundant if /auth/register is used, but ensures TLs can create users
    if session.exec(select(Employee).where(Employee.email == employee.email)).first():
        raise HTTPException(status_code=400, detail="Employee with this email already exists")

    hashed_pwd = get_password_hash(employee.password)
    # Ensure the role is validated (only allow 'employee' or 'team_leader')
    if employee.role.lower() not in ["employee", "team_leader"]:
        raise HTTPException(status_code=400, detail="Invalid role specified.")
        
    db_employee = Employee.model_validate(
        employee, 
        update={"hashed_password": hashed_pwd, "role": employee.role.lower()}
    )
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    return db_employee

# Read All (RESTRICTED TO TEAM LEADER)
@router.get("/", response_model=List[EmployeeRead])
def read_employees(
    session: SessionDep,
    # Requires Team Leader to view all employees
    user_data: dict = Depends(require_team_leader),
    skip: int = 0, 
    limit: int = 100, 
):
    return session.exec(select(Employee).offset(skip).limit(limit)).all()

# Read One (ALLOWED FOR SELF OR TEAM LEADER)
@router.get("/{employee_id}", response_model=EmployeeRead)
def read_employee(employee_id: int, session: SessionDep, current_user: CurrentEmployee):
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Check if user is the employee themselves OR a Team Leader
    if current_user.role == "team_leader" or current_user.id == employee_id:
        return employee
        
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied to view this profile.")

# Update (RESTRICTED TO TEAM LEADER)
@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee(
    employee_id: int, 
    employee_update: EmployeeUpdate, 
    session: SessionDep,
    user_data: dict = Depends(require_team_leader) # Requires Team Leader
):
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    # Only allow updating password via the dedicated field if present
    update_data = employee_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
    # Validation for role update
    if "role" in update_data and update_data["role"].lower() not in ["employee", "team_leader"]:
        raise HTTPException(status_code=400, detail="Invalid role specified.")
        
    employee.sqlmodel_update(update_data)
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


# Delete (RESTRICTED TO TEAM LEADER)
@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: int, 
    session: SessionDep,
    user_data: dict = Depends(require_team_leader) # Requires Team Leader
):
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    session.delete(employee)
    session.commit()
    return {"ok": True}
@router.post("/requests", response_model=ChangeRequestRead, status_code=status.HTTP_201_CREATED)
def submit_change_request(
    request: ChangeRequestCreate, 
    session: SessionDep, 
    current_user: CurrentEmployee
):
    """Allows an employee to submit a request to change their profile details."""
    
    # 1. Validate the field name (Employee cannot change role or password)
    allowed_fields = ["name", "email", "department"] 
    if request.field_name.lower() not in allowed_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Cannot request changes for field: {request.field_name}. Only {', '.join(allowed_fields)} are allowed."
        )

    # 2. Check for existing pending requests for this field/user
    existing_request = session.exec(
        select(EmployeeChangeRequest)
        .where(EmployeeChangeRequest.employee_id == current_user.id)
        .where(EmployeeChangeRequest.field_name == request.field_name.lower())
        .where(EmployeeChangeRequest.status == RequestStatus.PENDING)
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"A pending request for changing '{request.field_name}' already exists."
        )

    # 3. Create the request entry
    db_request = EmployeeChangeRequest(
        employee_id=current_user.id,
        field_name=request.field_name.lower(),
        new_value=request.new_value,
        status=RequestStatus.PENDING
    )
    
    session.add(db_request)
    session.commit()
    session.refresh(db_request)
    return db_request

# --- NEW: Employee Reads their own requests status ---
@router.get("/requests/mine", response_model=List[ChangeRequestRead])
def get_my_requests(session: SessionDep, current_user: CurrentEmployee):
    """Allows an employee to view the status of their submitted change requests."""
    return session.exec(
        select(EmployeeChangeRequest)
        .where(EmployeeChangeRequest.employee_id == current_user.id)
        .order_by(EmployeeChangeRequest.requested_at.desc())
    ).all()
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from models import EmployeeChangeRequest, Employee, RequestStatus
from schemas import ChangeRequestRead
from dependencies import require_team_leader, SessionDep
from datetime import datetime, timezone

router = APIRouter(prefix="/requests", tags=["Change Requests"])

# --- TL: Read All Pending Requests ---
@router.get("/", response_model=List[ChangeRequestRead])
def get_all_pending_requests(session: SessionDep, user_data: dict = Depends(require_team_leader)):
    """Team Leaders view all pending change requests."""
    return session.exec(
        select(EmployeeChangeRequest)
        .where(EmployeeChangeRequest.status == RequestStatus.PENDING)
        .order_by(EmployeeChangeRequest.requested_at.asc())
    ).all()

# --- TL: Approve/Reject Request ---
@router.put("/{request_id}/{action}", response_model=ChangeRequestRead)
def process_change_request(
    request_id: int, 
    action: str, # Must be 'approve' or 'reject'
    session: SessionDep, 
    team_leader_data: dict = Depends(require_team_leader) # Ensures only TL can access
):
    """Approves or rejects an employee change request and applies changes if approved."""
    
    # 1. Input Validation
    if action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'approve' or 'reject'.")

    # 2. Fetch and Validate Request
    db_request = session.get(EmployeeChangeRequest, request_id)
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found.")
    if db_request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Request already processed ({db_request.status}).")

    # 3. Process Action
    if action == "approve":
        employee = session.get(Employee, db_request.employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Target employee not found.")
            
        # A. Update Employee Detail (The core change)
        setattr(employee, db_request.field_name, db_request.new_value)
        session.add(employee)
        
        # B. Update Request Status
        db_request.status = RequestStatus.APPROVED
    
    else: # reject
        db_request.status = RequestStatus.REJECTED

    # 4. Finalize Request Record
    db_request.processed_by_id = team_leader_data.get("id") 
    db_request.processed_at = datetime.now(timezone.utc)
    
    session.add(db_request)
    session.commit()
    session.refresh(db_request)
    return db_request
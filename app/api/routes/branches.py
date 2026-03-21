from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.schemas.branch import BranchCreate, BranchResponse
from app.services import branch_service

router = APIRouter()


@router.post("/", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
def create_branch(payload: BranchCreate, db: Session = Depends(get_db)) -> BranchResponse:
    try:
        branch = branch_service.create_branch(db, payload)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except ConflictError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=e.detail) from e
    return BranchResponse.model_validate(branch)


@router.get("/", response_model=list[BranchResponse])
def list_branches(
    company_id: int = Query(..., description="Tenant filter (temporary until JWT context)."),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[BranchResponse]:
    try:
        branches = branch_service.list_branches_by_company(db, company_id=company_id, skip=skip, limit=limit)
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    return [BranchResponse.model_validate(b) for b in branches]

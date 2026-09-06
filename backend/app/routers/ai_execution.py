"""AI Execution Engine API router.

Provides endpoints for executing prompt packages and retrieving execution results.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user, require_auth
from app.schemas import (
    AIExecutionCreate,
    AIExecutionDetailOut,
    AIExecutionExecuteResponse,
    AIExecutionListOut,
    AIExecutionListResponse,
    AIExecutionOut,
    AIExecutionResponseOut,
)
from app.services.ai_execution.service import AIExecutionService

router = APIRouter(prefix="/ai", tags=["AI Execution"])


@router.post("/execute", response_model=AIExecutionExecuteResponse, status_code=201)
async def execute_prompt(
    data: AIExecutionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """Execute a prompt package against an AI provider.

    Requires authentication. The prompt package must belong to the authenticated user.
    """
    try:
        service = AIExecutionService(db)
        result = service.execute_prompt_package(
            user_id=current_user.id,
            prompt_package_id=data.prompt_package_id,
            provider=data.provider,
        )
        return AIExecutionExecuteResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions", response_model=AIExecutionListResponse)
async def list_executions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """List AI executions for the current user."""
    service = AIExecutionService(db)
    items, total = service.get_executions_by_user(
        current_user.id,
        skip=(page - 1) * size,
        limit=size,
    )
    return AIExecutionListResponse(
        items=[AIExecutionListOut.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/executions/{execution_id}", response_model=AIExecutionDetailOut)
async def get_execution(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """Get AI execution detail."""
    service = AIExecutionService(db)
    execution = service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return AIExecutionDetailOut.model_validate(execution)


@router.get("/executions/{execution_id}/response", response_model=AIExecutionResponseOut)
async def get_execution_response(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """Get the parsed response from an AI execution."""
    service = AIExecutionService(db)
    execution = service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    response = service.get_execution_response(execution_id)
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    return AIExecutionResponseOut(**response)

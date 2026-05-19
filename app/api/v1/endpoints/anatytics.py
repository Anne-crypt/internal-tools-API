from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.api.analytics import DepartmentCostResponse
from app.database import get_db
from app.controllers.analytics import analytics_controller

router = APIRouter()

@router.get(
    "/department-costs",
    response_model=DepartmentCostResponse,
    summary="Coûts par département",
)
async def get_department_costs(
    *,
    db: AsyncSession = Depends(get_db),
    sort_by: str = Query(
        "total_cost",
        description="Champ utilisé pour le tri",
        enum=["department", "total_cost", "tools_count", "total_users"]
    ),
    order: str = Query(
        "desc",
        description="Sens du tri (asc pour croissant, desc pour décroissant)",
        enum=["asc", "desc"]
    ),
) -> DepartmentCostResponse:
    """
    Récupère les coûts totaux par département, le nombre d'outils, d'utilisateurs,
    et une synthèse globale des coûts.
    """
    result = await analytics_controller.get_department_costs_summary(
        db=db, sort_by=sort_by, order=order
    )
    return result
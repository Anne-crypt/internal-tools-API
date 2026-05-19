from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.api.analytics import (
    DepartmentCostResponse,
    ExpensiveToolsResponse,
    ToolsByCategoryResponse,
)
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
        enum=["department", "total_cost", "tools_count", "total_users"],
    ),
    order: str = Query(
        "desc",
        description="Sens du tri (asc pour croissant, desc pour décroissant)",
        enum=["asc", "desc"],
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


@router.get(
    "/expensive-tools",
    response_model=ExpensiveToolsResponse,
    summary="Obtenir les outils les plus coûteux",
    description="Retourne la liste des outils les plus chers avec une analyse de leur efficacité et des opportunités de négociation pour Jennifer.",
)
async def get_expensive_tools(
    min_cost: float = Query(
        0.0,
        ge=0.0,
        description="Filtrer les outils ayant un coût mensuel supérieur ou égal à cette valeur",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Nombre maximum d'outils à retourner (maximum 100)",
    ),
    db: AsyncSession = Depends(get_db),
) -> ExpensiveToolsResponse:
    """
    Endpoint de Business Intelligence pour analyser l'efficacité financière des outils.
    """
    return await analytics_controller.get_expensive_tools(
        db=db, min_cost=min_cost, limit=limit
    )


@router.get(
    "/tools-by-category",
    response_model=ToolsByCategoryResponse,
    summary="Répartition des outils par catégorie",
    description="Retourne des statistiques agrégées par catégorie de logiciels (coût, utilisateurs, part du budget) ainsi que des insights business pour Alex.",
)
async def get_tools_by_category(
    db: AsyncSession = Depends(get_db),
) -> ToolsByCategoryResponse:
    """
    Endpoint de Business Intelligence pour analyser la stack technique par domaine/catégorie.
    """
    return await analytics_controller.get_tools_by_category(db=db)

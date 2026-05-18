from decimal import Decimal
from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.tool import tool_crud
from app.database import get_db
from app.schemas.api.tool import ToolPaginatedResponse

router = APIRouter()


@router.get("", response_model=ToolPaginatedResponse, summary="Filtrer et paginer les outils business")
async def get_tools(
    *,
    db: AsyncSession = Depends(get_db),
    department: str | None = Query(None, description="Filtrer par département (ex: Engineering)"),
    status: str | None = Query(None, description="Filtrer par statut (active, deprecated, trial)"),
    min_cost: Decimal | None = Query(None, description="Coût mensuel minimum"),
    max_cost: Decimal | None = Query(None, description="Coût mensuel maximum"),
    category: str | None = Query(None, alias="category", description="Nom de la catégorie (ex: Development)"),
    page: int = Query(1, ge=1, description="Numéro de la page"),
    limit: int = Query(10, ge=1, le=100, description="Nombre d'éléments par page"),
    sort_by: str = Query("name", description="Champ de tri (name, cost, date)"),
    sort_order: str = Query("asc", description="Sens du tri (asc, desc)")
) -> Any:
    """
    Récupère la liste des outils avec un filtrage multicritère,
    une pagination et un système de tri dynamique.
    """
    # On appelle notre fameuse méthode CRUD super musclée
    result = await tool_crud.get_filtered_tools(
        db,
        department=department,
        status=status,
        min_cost=min_cost,
        max_cost=max_cost,
        category_name=category,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return result